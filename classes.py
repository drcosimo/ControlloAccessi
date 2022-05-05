import asyncio
import string
import sys
import reactivex
from enums import *

class Gate():
    
    def __init__(self, idGate, gateName:GateName) -> None:
        self.idGate = idGate
        self.gateName = gateName
        self.executionMode = ExecutionMode.AUTOMATION_LOGGING
        self.lanes = []

    def appendLane(self,lane):
        self.lanes.append(lane)
    
    def getLane(self,index):
        try:
            return self.lanes[index]
        except IndexError as err:
            #print("out of range at Lane.getDevice({0})".format(index))
            return None

    def getLanes(self):
        return self.lanes

class Lane():

    def __init__(self,idLane,gate:Gate) -> None:
        self.devices = []
        self.idLane = idLane
        self.gate = gate
        self.laneStatus = LaneStatus.LANE_ACTIVE
        self.analyzerConnection = None

    def appendDevice(self,device):
        self.devices.append(device)

    def activateLane(self):
        self.laneStatus = LaneStatus.LANE_ACTIVE
    
    def deactivateLane(self):
        self.laneStatus = LaneStatus.LANE_NOT_ACTIVE

    def getLaneStatus(self) -> LaneStatus:
        return self.laneStatus

    def getDevices(self):
        return self.devices

    def getDevice(self,index):
        try:
            return self.devices[index]
        except IndexError as err:
            #print("out of range at Lane.getDevice({0})".format(index))
            return None
       

class TCPDevice():
    def __init__(self,ip,port,eventType:EventType,deviceType:DeviceType,lane:Lane) -> None:
        self.ip = ip
        self.port = port
        self.eventType = eventType
        self.deviceType = deviceType
        self.lane = lane
    
    def createObservable(self) -> reactivex.Observable:
        pass

class Event():
    def __init__(self,value,eventType,deviceType,lane) -> None:
        self.value = value
        self.deviceType = deviceType
        self.eventType = eventType
        self.lane = lane

    def toString(self) -> string:
        return "VALUE: {0}, EVENT: {1}, DEVICE: {2}, LANE: {3}".format(self.value,EventType(self.eventType).name,DeviceType(self.deviceType).name,self.lane.idLane)

class TCPServer(TCPDevice):
    def __init__(self, ip, port, eventType: EventType, deviceType: DeviceType,lane:Lane) -> None:
        super().__init__(ip, port, eventType, deviceType,lane)
    
    # funzione di creazione osservabile
    def createObservable(self) -> reactivex.Observable:
        def on_subscription(observer,scheduler):
            async def connect():       
                # creazione server
                server = await asyncio.start_server(handleClient,self.ip,self.port)
                # serve per un tempo indefinito
                await server.serve_forever()
            # client callback handler
            async def handleClient(reader:asyncio.StreamReader,writer:asyncio.StreamWriter):
                try:
                    peer = writer.get_extra_info("peername")
                    print("({0},{1}) serving {2}".format(self.ip,self.port,peer))
                    # acquisisco dati per un tempo indefinito
                    while True:
                        # chiusura connessione
                        if reader.at_eof():
                            break
                        # aspetto dato in arrivo
                        data = await reader.read(1024)
                        # decodifica dato
                        value = data.decode("utf-8")
                        # creazione evento 
                        event = Event(value,self.eventType,self.deviceType,self.lane)
                        #print("ottenuto {0} da {1}".format(event.toString(),peer))
                        # passo l'evento alla funzione on_next dell'observer
                        observer.on_next(event)
                    
                    # termino comunicazione 
                    writer.close()
                    await writer.wait_closed()
                    print("({0},{1}) serving, {2} disconnected".format(self.ip,self.port,peer))
                    # emissione eventi completata
                    observer.on_completed()

                except Exception as err:
                    print("({0},{1}) serving, connection with {2} interrupted".format(self.ip,self.port,peer))
                    #print(sys.call_tracing(sys.exc_info()[2],))
                    # passo l'errore all'observer
                    observer.on_error(sys.exc_info())
            # creazione task della funzione connect
            asyncio.create_task(connect())
        # creo un osservabile a partire dalla funzione che definisce la sorgente dei dati
        return reactivex.create(on_subscription)

class TCPClient(TCPDevice):

    def __init__(self, ip, port, eventType: EventType, deviceType: DeviceType, lane: Lane) -> None:
        super().__init__(ip, port, eventType, deviceType, lane)
    
    # funzione di creazione osservabile
    def createObservable(self) -> reactivex.Observable:
        def on_subscription(observer,scheduler):
            async def connect():
                # apertura connessione con il server
                reader,writer = await asyncio.open_connection(self.ip,self.port)
                # gestione comunicazione con il server
                await handleClient(reader,writer)
            # client callback handler
            async def handleClient(reader:asyncio.StreamReader,writer:asyncio.StreamWriter):
                try:
                    peer = writer.get_extra_info("peername")
                    print("({0},{1}) client, connected to {2}".format(self.ip,self.port,peer))
                    # acquisisco dati per un tempo indefinito
                    while True:
                        # chiusura connessione
                        if reader.at_eof():
                            break
                        # aspetto dato in arrivo
                        data = await reader.read(1024)
                        # decodifica dato
                        value = data.decode("utf-8")

                        # creazione evento 
                        event = Event(value,self.eventType,self.deviceType,self.lane)
                        # passo l'evento alla funzione on_next dell'observer
                        observer.on_next(event)
                        
                    # termino comunicazione 
                    writer.close()
                    await writer.wait_closed()
                    print("({0},{1}) client, {2} closed connection".format(self.ip,self.port,peer))
                    # emissione completata
                    observer.on_completed()
                except Exception as err:
                    print("({0},{1}) client, connection with {2} interrupted".format(self.ip,self.port,peer))
                    #print(sys.call_tracing(sys.exc_info()[2],))
                    # passo l'errore all'observer
                    observer.on_error(sys.exc_info())

            # creazione task della funzione connect
            asyncio.create_task(connect())
        # creo un osservabile a partire dalla funzione che definisce la sorgente dei dati
        return reactivex.create(on_subscription)

class FrontCam(TCPServer):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port,EventType.PLATE,DeviceType.FRONT_CAM,lane)

class RearCam(TCPServer):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port, EventType.PLATE, DeviceType.REAR_CAM,lane)

class Rfid(TCPClient):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port, EventType.BADGE, DeviceType.RFID,lane)

class Button(TCPServer):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port, EventType.HUMAN_ACTION, DeviceType.BUTTON,lane)

class Bar(TCPClient):
    def __init__(self, ip, port, eventType: EventType, deviceType: DeviceType, lane: Lane) -> None:
        super().__init__(ip, port, EventType.OPEN_GATE, DeviceType.BAR, lane)

class TestAnalyzer(reactivex.Observable):

    def __init__(self,lane) -> None:
        self.lane = lane
        super().__init__()

    def on_next(self, event) -> None:
        pass
        #print("{0}".format(event.toString()))
    
    def on_completed(self) -> None:
        pass
        #print("daje")
    
    def on_error(self, error: Exception) -> None:
        pass
        #print("errore:{0}".format(error))

class Connection():
    def __init__(self,db_ip,db_port,bar_ip,bar_port,logger_ip,logger_port) -> None:
        self.dp_ip = db_ip
        self.db_port = db_port
        self.bar_ip = bar_ip
        self.bar_port = bar_port
        self.logger_ip = logger_ip
        self.logger_port = logger_port


    async def connectToDb(self,req):
        r,w = await asyncio.open_connection(self.dp_ip,self.db_port)
        w.write(req.encode("utf-8"))
        await w.drain()

        w.close()
        await w.wait_closed()
    
    async def connectToBar(self):
        r,w = await asyncio.open_connection(self.bar_ip,self.bar_port)
        w.write("OPEN_GATE".encode("utf-8"))
        await w.drain()

        w.close()
        await w.wait_closed()

    def dbRequest(self,plate,badge,time):
        # richiesta grant badgeplate
        req = f"{plate},{badge},{time}"
        
        asyncio.create_task(self.connectToDb(req))

    def loggerRequest(self, evt: Event):
        req = f"{evt.value},{evt.eventType},{evt.deviceType}"

        asyncio.create_task(self.connectToLogger(req))

    async def connectToLogger(self, evt):
        r, w = await asyncio.open_connection(self.logger_ip, self.logger_port)
        w.write(evt.encode("utf-8"))
        await w.drain()

        w.close()
        await w.wait_closed()