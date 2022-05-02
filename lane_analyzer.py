import asyncio
from datetime import datetime
import sys

import reactivex
from custom_errors import AlreadyInitialized
from reactivex import Observable, Subject

from enums import *
from classes import Connection,Event

class TransitAnalyzer(Subject):
    def __init__(self):
        self.actualPlate = None
        self.actualBadge = None
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.connections = Connection()
        self.startTimeTransit = None
        self.endTimeTransit = None
        self.logObject= None

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
                        event = Event(f"{tmp[0]},{tmp[1]}", tmp[2], tmp[3])
                    elif len(tmp) > 2:
                        event = Event(tmp[0], tmp[1], tmp[2])
                    elif len(tmp) > 1:
                        event = Event(None, tmp[0], tmp[1])

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

    def on_next(self, event:Event):
        if event is not None:
            self.analyze(event)
        else:
            raise TypeError("L'evento passato risulta NULL")


    def on_error(self, error):
        print(f"E' stato rilevato un errore: {error}")    # TODO: Gestire tramite console oppure tramite logger?


    def on_completed(self):
        print("Evento completato")    # TODO: Gestire tramite console oppure tramite logger?

    
    def analyze(self, event:Event): # TODO: aggiungere il tipo all'event

        # ----------------------------------------------------
        # waiting for transit q0
        # ----------------------------------------------------
        if self.transitState == TransitState.WAIT_FOR_TRANSIT:
            # controllo tipo evento
            if event.eventType == EventType.HUMAN_ACTION:
                self.connections.loggerRequest(event)
                self.transitState = TransitState.GRANT_OK
            elif event.eventType == EventType.PLATE:
                self.connections.loggerRequest(event)
                self.actualPlate = event.value
            elif event.eventType == EventType.BADGE:
                self.connections.loggerRequest(event)
                self.actualBadge = event.value
            
            # passo al secondo stato
            self.transitState = TransitState.TRANSIT_STARTED
                
        # ----------------------------------------------------
        # transit started q1
        # ----------------------------------------------------
        if self.transitState == TransitState.TRANSIT_STARTED:
            # TODO aggiungere ritardo
            if event.eventType == EventType.HUMAN_ACTION:
                self.connections.loggerRequest(event)
                self.transitState = TransitState.GRANT_OK
            # salvo anche il badge se è arrivato
            elif event.eventType == EventType.BADGE and self.actualPlate != None:
                self.actualBadge = event.value
                self.transitState = TransitState.GRANT_REQ_BADGEPLATE
            # salvo anche la plate se è arrivata
            elif event.eventType == EventType.PLATE and self.actualBadge != None:
                self.actualPlate = event.value
                self.transitState = TransitState.GRANT_REQ_BADGEPLATE
            else:
                self.transitState = TransitState.GRANT_REQ

        # ----------------------------------------------------
        # grant request q2
        # ----------------------------------------------------
        if self.transitState == TransitState.GRANT_REQ:
            if event.eventType == EventType.HUMAN_ACTION:
                self.connections.loggerRequest(event)
                self.transitState = TransitState.GRANT_OK
            else:   
                # richiesta al db
                self.connections.dbRequest(RequestType.POLICY,[self.actualPlate,self.actualBadge,self.startTimeTransit])
                self.transitState = TransitState.WAIT_FOR_RESPONSE
        
        # ----------------------------------------------------
        # wait for response q3
        # ----------------------------------------------------
       
        if self.transitState == TransitState.WAIT_FOR_RESPONSE:
            if event.eventType == EventType.HUMAN_ACTION:
                self.connections.loggerRequest(event)
                self.transitState = TransitState.GRANT_OK
            # no policy found
            elif event.eventType == EventType.NO_POLICY:
                self.connections.loggerRequest(event)
                self.transitState = TransitState.GRANT_REFUSED
            elif (event.eventType == EventType.ONLY_PLATE_POLICY and event.value.split(",")[0] == self.actualPlate) or (event.eventType == EventType.ONLY_BADGE_POLICY and event.value.split(",")[1] == self.actualBadge):
                self.connections.loggerRequest(event)
                # grant ok
                self.transitState = TransitState.GRANT_OK
            elif (event.eventType == EventType.BADGE_PLATE_POLICY) or (event.eventType == EventType.ONLY_PLATE_POLICY and self.actualPlate is None) or (event.eventType == EventType.ONLY_BADGE_POLICY and self.actualBadge is None):
                # richiesta accoppiata badge plate
                if self.actualBadge != None and self.actualPlate != None:
                    self.transitState = TransitState.GRANT_REQ_BADGEPLATE
                else:
                    # ho bisogno di un badge o una plate per procedere
                    self.transitState = TransitState.WAIT_FOR_DATA
        # ----------------------------------------------------
        # wait for data q
        # ----------------------------------------------------
       
        if self.transitState == TransitState.WAIT_FOR_DATA:
            # TODO aggiungere timeout
            if event.eventType == EventType.HUMAN_ACTION:
                self.connections.loggerRequest(event)
                self.transitState = TransitState.GRANT_OK    
            elif self.actualPlate != None and event.eventType == EventType.BADGE:
                self.actualBadge = event.value
                self.transitState = TransitState.GRANT_REQ_BADGEPLATE
            elif self.actualBadge != None and event.eventType == EventType.PLATE:
                self.actualPlate = event.value
                self.transitState = TransitState.GRANT_REQ_BADGEPLATE
        
        # ----------------------------------------------------
        # richiesta accoppiata badge plate
        # ----------------------------------------------------
       
        if self.transitState == TransitState.GRANT_REQ_BADGEPLATE:
            if event.eventType == EventType.HUMAN_ACTION:
                self.connections.loggerRequest(event)
                self.transitState = TransitState.GRANT_OK    
            else:
                # richiesta grant badgeplate
                args = [self.actualPlate,self.actualBadge,self.startTimeTransit]
                self.connections.dbRequest(RequestType.FIND_PLATE_BADGE,args)
                self.transitState = TransitState.GRANT_RES_BADGEPLATE
            
        # ----------------------------------------------------
        # risposta accoppiata badge plate
        # ----------------------------------------------------
       
        if self.transitState == TransitState.GRANT_RES_BADGEPLATE:
            if event.eventType == EventType.BADGE_PLATE_OK or event.eventType == EventType.HUMAN_ACTION:
                self.connections.loggerRequest(event)
                self.transitState = TransitState.GRANT_OK
            elif event.eventType == EventType.NO_GRANT:
                self.connections.loggerRequest(event)
                self.transitState = TransitState.GRANT_REFUSED
        
        # ----------------------------------------------------
        # accesso garantito,apertura sbarra
        # ----------------------------------------------------
        if self.transitState == TransitState.GRANT_OK:
            # connessione alla sbarra
            asyncio.create_task(self.connections.connectToBar())
            # inserimento transit history con almeno un dato
            if self.actualBadge != None or self.actualPlate != None:
                self.endTimeTransit = datetime.now()
                # inserimento transit history
                args = [self.actualPlate,self.actualBadge,self.endTimeTransit]
                self.connections.dbRequest(RequestType.INSERT_TRANSIT_HISTORY,args)
            # end transit
            self.transitState = TransitState.END_TRANSIT
        
        # ----------------------------------------------------
        # accesso non consentito
        # ----------------------------------------------------
        if self.transitState == TransitState.GRANT_REFUSED:
            if event.eventType == EventType.HUMAN_ACTION:
                self.connections.loggerRequest(event)
                self.transitState = TransitState.GRANT_OK
            else:
                self.transitState = TransitState.END_TRANSIT

        # ----------------------------------------------------
        # fine transito, ritorno stato iniziale
        # ----------------------------------------------------
        if self.transitState == TransitState.END_TRANSIT:
            self.cleanAnalyzer()

    def cleanAnalyzer(self):
        self.actualBadge = None
        self.actualPlate = None
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.startTimeTransit = None
        self.endTimeTransit = None