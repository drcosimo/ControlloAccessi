from utils.enums import *
from model.TCPDevice import TCPDevice
from model.Lane import Lane
from reactivex import Observable, create
import asyncio
from model.Event import Event
import sys

class TCPClient(TCPDevice):

    def __init__(self, ip, port, eventType: EventType, deviceType: DeviceType, lane: Lane) -> None:
        super().__init__(ip, port, eventType, deviceType, lane)
    
    # funzione di creazione osservabile
    def createObservable(self) -> Observable:
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
        return create(on_subscription)