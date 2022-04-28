import asyncio
from datetime import datetime

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
            async def log():
                try:
                    while True:
                        # inizializzo variabile di stato
                        self.logObject = None
                        # aspetto che l'evento venga reso disponibile dall'analyzer
                        while self.logObject is None:
                            await asyncio.sleep(0)
                        # emetto l'evento al logger
                        observer.on_next(self.logObject)
                except Exception as err:
                    observer.on_error(err)
            asyncio.create_task(log())        
        return reactivex.create(on_subscription)

    def emettiLogger(self,event:EventType):
        self.logObject = event

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
        # emissione evento al logger
        self.emettiLogger(event)

        # ----------------------------------------------------
        # waiting for transit q0
        # ----------------------------------------------------
        if self.transitState == TransitState.WAIT_FOR_TRANSIT:
            # controllo tipo evento
            if event.eventType == EventType.HUMAN_ACTION:
                self.emettiLogger(event)
                self.transitState = TransitState.GRANT_OK
            elif event.eventType == EventType.PLATE:
                self.emettiLogger(event)
                self.actualPlate = event.value
            elif event.eventType == EventType.BADGE:
                self.emettiLogger(event)
                self.actualBadge = event.value
            
            # passo al secondo stato
            self.transitState = TransitState.TRANSIT_STARTED
                
        # ----------------------------------------------------
        # transit started q1
        # ----------------------------------------------------
        if self.transitState == TransitState.TRANSIT_STARTED:
            # TODO aggiungere ritardo
            if event.eventType == EventType.HUMAN_ACTION:
                self.emettiLogger(event)
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
                self.emettiLogger(event)
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
                self.transitState = TransitState.GRANT_OK
            # no policy found
            elif event.eventType == EventType.NO_POLICY:
                self.emettiLogger(event)
                self.transitState = TransitState.GRANT_REFUSED
            elif (event.eventType == EventType.ONLY_PLATE_POLICY and event.value.split(",")[0] == self.actualPlate) or (event.eventType == EventType.ONLY_BADGE_POLICY and event.value.split(",")[1] == self.actualBadge):
                self.emettiLogger(event)
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
                self.emettiLogger(event)
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
                self.emettiLogger(event)
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
                self.emettiLogger(event)
                self.transitState = TransitState.GRANT_OK
            elif event.eventType == EventType.NO_GRANT:
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
                self.emettiLogger(event)
                self.transitState = TransitState.GRANT_OK
            else:
                self.transitState = TransitState.END_TRANSIT

        # ----------------------------------------------------
        # fine transito, ritorno stato iniziale
        # ----------------------------------------------------
        if self.transitState == TransitState.END_TRANSIT:
            self.emettiLogger(None)
            self.cleanAnalyzer()

    def cleanAnalyzer(self):
        self.actualBadge = None
        self.actualPlate = None
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.startTimeTransit = None
        self.endTimeTransit = None