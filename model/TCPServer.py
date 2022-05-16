from utils.enums import *
from model.TCPDevice import TCPDevice
from model.Lane import Lane
from reactivex import Observable, create
import asyncio
from model.Event import Event
import sys

class TCPServer(TCPDevice):
    def __init__(self, ip, port, eventType: EventType, deviceType: DeviceType,lane:Lane) -> None:
        super().__init__(ip, port, eventType, deviceType,lane)
    
    # funzione di creazione osservabile
    def createObservable(self) -> Observable:
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
        return create(on_subscription)