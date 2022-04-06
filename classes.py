import asyncio
import string
import reactivex
from enums import *

class Gate():
    lanes = []
    def __init__(self, idGate, gateName:GateName) -> None:
        self.idGate = idGate
        self.gateName = gateName
    
    def appendLane(self,lane):
        self.lanes.append(lane)
    
    def getLane(self,index):
        try:
            return self.lanes[index]
        except IndexError as err:
            print("out of range at Lane.getDevice({0})".format(index))
            return None

    def getLanes(self):
        return self.lanes

class Lane():
    laneStatus:LaneStatus = LaneStatus.LANE_NOT_ACTIVE
    devices = []

    def __init__(self,idLane,gate:Gate) -> None:
        self.idLane = idLane
        self.gate = gate
    
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
            print("out of range at Lane.getDevice({0})".format(index))
            return None
       

class TCPDevice():
    def __init__(self,ip,port,eventType:EventType,deviceType:DeviceType,lane:Lane) -> None:
        self.ip = ip
        self.port = port
        self.eventType = eventType
        self.deviceType = deviceType
        self.lane = lane

class Event():
    def __init__(self,value,eventType,deviceType) -> None:
        self.value = value
        self.deviceType = deviceType
        self.eventType = eventType

    def toString(self) -> string:
        return "VALUE: {0}, EVENT: {1}, DEVICE: {2}".format(self.value,self.eventType,self.deviceType)

class TCPServer(TCPDevice):
    def __init__(self, ip, port, eventType: EventType, deviceType: DeviceType,lane:Lane) -> None:
        super().__init__(ip, port, eventType, deviceType,lane)
    
    # funzione di creazione osservabile
    def createObservable(self) -> reactivex.Observable:
        def on_subscription(observer,scheduler):
            async def connect(self):       
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
                        event = Event(value,self.eventType,self.deviceType)
                        print("ottenuto {0} da {1}".format(event.toString(),peer))
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
                    # passo l'errore all'observer
                    observer.on_error(err)
            # creazione task della funzione connect
            asyncio.create_task(connect(self))
        # creo un osservabile a partire dalla funzione che definisce la sorgente dei dati
        return reactivex.create(on_subscription)

class TCPClient(TCPDevice):
    retry = 1

    def __init__(self, ip, port, eventType: EventType, deviceType: DeviceType, lane: Lane) -> None:
        super().__init__(ip, port, eventType, deviceType, lane)
    
    # funzione di creazione osservabile
    def createObservable(self) -> reactivex.Observable:
        def on_subscription(observer,scheduler):
            async def connect(self):
                # apertura connessione con il server
                reader,writer = await asyncio.open_connection(self.ip,self.port)
                # gestione comunicazione con il server
                asyncio.create_task(handleClient(reader,writer))
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
                        data = await reader.readline()
                        # decodifica dato
                        value = data.decode("utf-8")
                        # creazione evento 
                        event = Event(value,self.eventType,self.deviceType)
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
                    # riprovo a connettermi una volta
                    if self.retry == 1:
                        self.retry = 0
                        asyncio.create_task(connect(self))
                    else:
                        # passo l'errore all'observer
                        observer.on_error(err)

            # creazione task della funzione connect
            asyncio.create_task(connect(self))
        # creo un osservabile a partire dalla funzione che definisce la sorgente dei dati
        return reactivex.create(on_subscription)

class FrontCam(TCPServer):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port,EventType.READ_VEHICLE_CREDENTIAL,DeviceType.FRONT_CAM,lane)

class RearCam(TCPServer):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port, EventType.READ_VEHICLE_CREDENTIAL, DeviceType.REAR_CAM,lane)

class Rfid(TCPClient):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port, EventType.READ_PERSON_CREDENTIAL, DeviceType.RFID,lane)

class Button(TCPServer):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port, EventType.HUMAN_ACTION, DeviceType.BUTTON,lane)


class TestAnalyzer(reactivex.Observable):
    def __init__(self,lane) -> None:
        self.lane = lane
        super().__init__()

    def on_next(self, event) -> None:
        print("{0}".format(event.toString()))
    
    def on_completed(self) -> None:
        print("daje")
    
    def on_error(self, error: Exception) -> None:
        print("errore:{0}".format(error))


''' TODO
# classi observer => Analyzer, Logger
'''

''' TODO
# classe di interfacciamento con il db => tutte le chiamate al db saranno 
# fatte tramite metodi di questa classe 
'''