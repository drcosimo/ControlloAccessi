import asyncio
from datetime import datetime
from custom_errors import AlreadyInitialized
from reactivex import Subject

from enums import *
from classes import Connection,Event

class TransitAnalyzer(Subject):
    def __init__(self, conn:Connection):
        self.actualPlate = None
        self.actualBadge = None
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.connections = conn
        self.startTimeTransit = None
        self.endTimeTransit = None
    
    # Funzione che ha il compito di di assegnare un valore alla targa se essa non ha ancora un valore
    def setActualPlate(self, plate):
        if self.actualPlate is None:
            self.actualPlate = plate
        elif self.actualPlate != plate:
            raise AlreadyInitialized("E' stato già assegnato un valore alla targa")


    # Funzione che ha il compito di di assegnare un valore al badge se esso non ha ancora un valore
    def setActualBadge(self, badge):
        if self.actualBadge is None:
            self.setActualBadge = badge
        else:
            raise AlreadyInitialized("E' stato già assegnato un valore al badge")

    def setActualPolicy(self,policy):
        if self.actualPolicy is None:
            self.setActualPolicy = policy
        else:
            raise AlreadyInitialized("E' stato già assegnato un valore alla policy")
    
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
        print("ANALYZER - {0}, STATE: {1}".format(event.toString(),self.transitState))

        # ----------------------------------------------------
        # waiting for transit q0
        # ----------------------------------------------------
        if self.transitState == TransitState.WAIT_FOR_TRANSIT:
            # controllo tipo evento
            if event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK
            elif event.eventType == EventType.PLATE:
                self.actualPlate = event.value
            elif event.eventType == EventType.BADGE:
                self.actualBadge = event.value
            
            # passo al secondo stato
            self.transitState = TransitState.TRANSIT_STARTED
                
        # ----------------------------------------------------
        # transit started q1
        # ----------------------------------------------------
        if self.transitState == TransitState.TRANSIT_STARTED:
            # TODO aggiungere ritardo

            if event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK
            # salvo anche il badge se è arrivato
            elif event.eventType == EventType.BADGE and self.actualPlate != None:
                self.setActualBadge(event.value)
                self.transitState = TransitState.GRANT_REQ_BADGEPLATE
            # salvo anche la plate se è arrivata
            elif event.eventType == EventType.PLATE and self.actualBadge != None:
                self.setActualPlate(event.value)
                self.transitState = TransitState.GRANT_REQ_BADGEPLATE
            else:
                self.transitState = TransitState.GRANT_REQ

        # ----------------------------------------------------
        # grant request q2
        # ----------------------------------------------------
        if self.transitState == TransitState.GRANT_REQ:
            if event.eventType == EventType.HUMAN_ACTION:
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
                self.transitState = TransitState.GRANT_REFUSED
            elif (event.eventType == EventType.ONLY_PLATE_POLICY and event.value.strip(",")[0] == self.actualPlate) or (event.eventType == EventType.ONLY_BADGE_POLICY and event.value.strip(",")[1] == self.actualBadge):
                # grant ok
                self.transitState = TransitState.GRANT_OK
            else:
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
                self.transitState = TransitState.GRANT_OK    
            elif self.actualPlate != None and event.eventType == EventType.BADGE:
                self.setActualBadge(event.value)
                self.transitState = TransitState.GRANT_REQ_BADGEPLATE
            elif self.actualBadge != None and event.eventType == EventType.PLATE:
                self.setActualPlate(event.value)
                self.transitState = TransitState.GRANT_REQ_BADGEPLATE
        
        # ----------------------------------------------------
        # richiesta accoppiata badge plate
        # ----------------------------------------------------
       
        if self.transitState == TransitState.GRANT_REQ_BADGEPLATE:
            if event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK    
            else:
                # richiesta grant badgeplate
                self.connections.dbRequest(RequestType.FIND_PLATE_BADGE,[self.actualPlate,self.actualBadge,self.startTimeTransit])
                self.transitState = TransitState.GRANT_RES_BADGEPLATE
            
        # ----------------------------------------------------
        # risposta accoppiata badge plate
        # ----------------------------------------------------
       
        if self.transitState == TransitState.GRANT_RES_BADGEPLATE:
            if event.eventType == EventType.BADGE_PLATE_OK or event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK
            elif event.eventType == EventType.NO_GRANT:
                self.transitState = TransitState.GRANT_REFUSED
        
        # ----------------------------------------------------
        # accesso garantito,apertura sbarra
        # ----------------------------------------------------
        if self.transitState == TransitState.GRANT_OK:
            # connessione alla sbarra
            asyncio.create_task(self.connections.connectToBar())
            # end transit
            self.transitState = TransitState.END_TRANSIT
        
        # ----------------------------------------------------
        # accesso non consentito
        # ----------------------------------------------------
        if self.transitState == TransitState.GRANT_REFUSED:
            if event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK
            else:
                self.transitState = TransitState.END_TRANSIT

        # ----------------------------------------------------
        # fine transito, ritorno stato iniziale
        # ----------------------------------------------------
        if self.transitState == TransitState.END_TRANSIT:
            self.endTimeTransit = datetime.now()
            # inserimento transit history
            args = [self.actualPlate,self.actualBadge,self.endTimeTransit]
            self.connections.dbRequest(RequestType.INSERT_TRANSIT_HISTORY,args)
            self.cleanAnalyzer()

    def cleanAnalyzer(self):
        self.actualPlate = None
        self.actualBadge = None
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.startTimeTransit = None
        self.endTimeTransit = None