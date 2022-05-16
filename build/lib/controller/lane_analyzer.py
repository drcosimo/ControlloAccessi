import asyncio
import sys
from reactivex import Observable, Subject
import reactivex

from utils.enums import *
from model.Event import Event

class TransitAnalyzer(Subject):
    def __init__(self,connection,lane):
        self.actualPlate = None
        self.actualBadge = None
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.connections = connection
        self.startTimeTransit = None
        self.endTimeTransit = None
        self.startedWith = None
        self.lastPlate = None
        self.lastBadge = None
        self.lane = lane

    def on_next(self, event:Event):
        if event is not None:
            asyncio.create_task(self.analyze(event))
        else:
            raise TypeError("L'evento passato risulta NULL")


    def on_error(self, error):
        print(f"E' stato rilevato un errore: {error}")    # TODO: Gestire tramite console oppure tramite logger?


    def on_completed(self):
        print("Evento completato")    # TODO: Gestire tramite console oppure tramite logger?

    def prettyPrint(self,evt:Event,state):
        log = "ANALYZER-{0}--stato:{1}".format(evt.toString(),TransitState(state).name)
        
        if evt.eventType == EventType.TIMED_OUT:
            print('\x1b[38;5;196m'+ log +'\033[0m')
        elif evt.lane.idLane == 1:
            print('\033[94m'+ log +'\033[0m')
        else:
            print('\033[92m'+ log +'\033[0m')

    async def timeout(self):
        await asyncio.sleep(120)

        if self.transitState == TransitState.WAIT_FOR_DATA:
                evt = Event(self.startedWith,EventType.TIMED_OUT,DeviceType.ANALYZER,self.lane)
                self.connections.loggerRequest(evt)
                self.prettyPrint(evt,self.transitState)
                self.cleanAnalyzer()
        else:
            try:
                asyncio.current_task().cancel()
            except asyncio.CancelledError:
                pass

    # metodo per l'emissione dati al logger
    def createObservable(self) -> Observable:
        def on_subscription(observer,scheduler):
            async def connect():
                # apertura connessione con il server
                server = await asyncio.start_server(handleClient, self.connections.logger_ip,self.connections.logger_port)
                # gestione comunicazione con il server
                await server.serve_forever()
            # client callback handler
            async def handleClient(reader:asyncio.StreamReader,writer:asyncio.StreamWriter):
                try:
                    # aspetto dato in arrivo
                    data = await reader.read(1024)
                    # decodifica dato
                    value = data.decode("utf-8")
                    tmp = value.split(",")

                    if len(tmp) > 3:
                        event = Event(f"{tmp[0]},{tmp[1]}", int(tmp[2]), int(tmp[3]), self.lane)
                    elif len(tmp) > 2:
                        event = Event(tmp[0], int(tmp[1]), int(tmp[2]), self.lane)
                    elif len(tmp) > 1:
                        event = Event(None, int(tmp[0]), int(tmp[1]), self.lane)

                    # passo l'evento alla funzione on_next dell'observer
                    observer.on_next(event)
                        
                    # termino comunicazione 
                    writer.close()
                    await writer.wait_closed()
                except Exception as err:
                    #print("({0},{1}) client, connection with {2} interrupted".format(self.ip,self.port,peer))
                    #print(sys.call_tracing(sys.exc_info()[2],))
                    # passo l'errore all'observer
                    observer.on_error(sys.exc_info())

            # creazione task della funzione connect
            asyncio.create_task(connect())
        # creo un osservabile a partire dalla funzione che definisce la sorgente dei dati
        return reactivex.create(on_subscription)
            
    
    async def analyze(self, event:Event):

        self.connections.loggerRequest(event)

        # ----------------------------------------------------
        # waiting for transit q0
        # ----------------------------------------------------
        if self.transitState == TransitState.WAIT_FOR_TRANSIT:
            self.prettyPrint(event,self.transitState)
            # controllo tipo evento
            if event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK
            elif event.eventType == EventType.PLATE and event.value != self.lastPlate:
                self.actualPlate = event.value
                self.startedWith = event.value
                 # passo al secondo stato
                self.transitState = TransitState.TRANSIT_STARTED
            elif event.eventType == EventType.BADGE and event.value != self.lastBadge:
                self.actualBadge = event.value
                self.startedWith = event.value
                # passo al secondo stato
                self.transitState = TransitState.TRANSIT_STARTED
                 
        # ----------------------------------------------------
        # transit started q1
        # ----------------------------------------------------
        if self.transitState == TransitState.TRANSIT_STARTED:
            self.prettyPrint(event,self.transitState)
            # TODO aggiungere ritardo
            if event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK
            # salvo anche il badge se è arrivato
            elif event.eventType == EventType.BADGE and self.actualPlate != None:
                self.actualBadge = event.value
            # salvo anche la plate se è arrivata
            elif event.eventType == EventType.PLATE and self.actualBadge != None:
                self.actualPlate = event.value
            
            self.transitState = TransitState.DB_REQ

        # ----------------------------------------------------
        # grant request q2
        # ----------------------------------------------------
        if self.transitState == TransitState.DB_REQ:
            self.prettyPrint(event,self.transitState)
            if event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK
            else:
                # richiesta al db
                self.connections.dbRequest(self.actualPlate,self.actualBadge,self.startTimeTransit)
                self.transitState = TransitState.DB_RES
        
        # ----------------------------------------------------
        # wait for response q3
        # ----------------------------------------------------
       
        if self.transitState == TransitState.DB_RES:
            self.prettyPrint(event,self.transitState)
            if event.eventType == EventType.HUMAN_ACTION :
                self.transitState = TransitState.GRANT_OK
            else:    
                if event.eventType == EventType.GRANT_OK:
                    self.transitState = TransitState.GRANT_OK
                elif event.eventType == EventType.GRANT_REFUSED:
                    self.transitState = TransitState.GRANT_REFUSED
                elif event.eventType == EventType.NEED_PLATE or event.eventType == EventType.NEED_BADGE:
                    self.transitState = TransitState.WAIT_FOR_DATA
        
        # ----------------------------------------------------
        # wait for data q
        # ----------------------------------------------------
       
        if self.transitState == TransitState.WAIT_FOR_DATA:
            self.prettyPrint(event,self.transitState)

            # metodo di timeout
            asyncio.create_task(self.timeout())
            
            if event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK
            elif self.actualPlate != None and event.eventType == EventType.BADGE:
                self.actualBadge = event.value
                self.transitState = TransitState.DB_REQ
            elif self.actualBadge != None and event.eventType == EventType.PLATE:
                self.actualPlate = event.value
                self.transitState = TransitState.DB_REQ
        
        # ----------------------------------------------------
        # accesso garantito,apertura sbarra
        # ----------------------------------------------------
        if self.transitState == TransitState.GRANT_OK:
            self.prettyPrint(event,self.transitState)
            # connessione alla sbarra
            await self.connections.connectToBar()
            # end transit
            self.transitState = TransitState.END_TRANSIT
        
        # ----------------------------------------------------
        # accesso non consentito
        # ----------------------------------------------------
        if self.transitState == TransitState.GRANT_REFUSED:
            self.prettyPrint(event,self.transitState)
            if event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK
            else:
                self.transitState = TransitState.END_TRANSIT

        # ----------------------------------------------------
        # fine transito, ritorno stato iniziale
        # ----------------------------------------------------
        if self.transitState == TransitState.END_TRANSIT:
            self.prettyPrint(event,self.transitState)
            self.cleanAnalyzer()

    def cleanAnalyzer(self):
        self.lastPlate = self.actualPlate
        self.lastBadge = self.actualBadge
        self.actualBadge = None
        self.actualPlate = None
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.startTimeTransit = None
        self.endTimeTransit = None
        self.startedWith = None