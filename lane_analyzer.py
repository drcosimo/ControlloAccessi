import asyncio
from datetime import datetime
from multiprocessing import Event
from database.custom_errors import AlreadyInitialized, CustomErrors
from reactivex import Subject

from enums import *

class TransitAnalyzer(Subject):

    def __init__(self, plate, badge,policy):
        self.actualPlate = plate
        self.actualBadge = badge
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.actualPolicy = policy
        
    async def connectToDb(self,req):
        r,w = await asyncio.open_connection(DB_IP,DB_PORT)
        w.write(req.encode("utf-8"))
        await w.drain()

        w.close()
        await w.wait_closed()
    async def connectToBar(self):
        r,w = await asyncio.open_connection(BAR_IP,BAR_PORT)
        w.write("OPEN_GATE".encode("utf-8"))
        await w.drain()

        w.close()
        await w.wait_closed()

    def dbRequest(self,reqType,reqArgs):
        # richiesta grant badgeplate
        req = "{0}".format(reqType)
        for arg in reqArgs:
            req += ",{0}".format(arg)
   
        asyncio.create_task(self.connectToDb(req))

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
    
    def on_next(self, event):
        if event is not None:
            self.analyze(event)
        else:
            raise TypeError("L'evento passato risulta NULL")


    def on_error(self, error):
        print(f"E' stato rilevato un errore: {error}")    # TODO: Gestire tramite console oppure tramite logger?


    def on_completed(self):
        print("Evento completato")    # TODO: Gestire tramite console oppure tramite logger?

    
    def analyze(self, event:Event): # TODO: aggiungere il tipo all'event
        self.startTimeTransit = datetime.now()

        # intervento umano
        if event.eventType == EventType.HUMAN_ACTION:
            self.transitState = TransitState.MANUAL_GRANT_OK
        
        if self.transitState == TransitState.MANUAL_GRANT_OK:
            self.transitState = TransitState.GRANT_OK

        # waiting for transit
        if self.transitState == TransitState.WAIT_FOR_TRANSIT:
            # controllo tipo evento
            if event.eventType == EventType.PLATE:
                # passo al secondo stato
                self.transitState = TransitState.TRANSIT_STARTED_PLATE
                self.actualPlate = event.value
            elif event.eventType == EventType.BADGE:
                self.transitState = TransitState.TRANSIT_STARTED_BADGE
                self.actualBadge = event.value

        # transit started
        if self.transitState == TransitState.TRANSIT_STARTED_PLATE:
            # salvo il badge se è arrivato
            if event.eventType == EventType.BADGE:
                self.setActualBadge(event.value)

            # prossimo stato
            self.transitState = TransitState.GRANT_REQ_PLATE

        if self.transitState == TransitState.TRANSIT_STARTED_BADGE:
            # salvo il badge se è arrivato
            if event.eventType == EventType.PLATE:
                self.setActualBadge(event.value)

            # prossimo stato
            self.transitState = TransitState.GRANT_REQ_BADGE
        
        # grant request for plate
        if self.transitState == TransitState.GRANT_REQ_PLATE:
            # richiesta al db
            self.dbRequest(RequestType.POLICY_FROM_PLATE,[self.actualPlate,self.startTimeTransit])
            self.transitState = TransitState.WAIT_FOR_POLICY_PLATE
        
        # grant request for badge
        if self.transitState == TransitState.GRANT_REQ_BADGE:
            # richiesta al db
            self.dbRequest(RequestType.POLICY_FROM_BADGE,[self.actualBadge,self.startTimeTransit])
            self.transitState = TransitState.WAIT_FOR_POLICY_BADGE

        # wait for policy
        if self.transitState == TransitState.WAIT_FOR_POLICY_PLATE:
            
            if event.eventType == EventType.ONLY_PLATE_POLICY and event.value.strip(",")[0] == self.actualPlate:
                # grant ok
                self.transitState = TransitState.GRANT_OK
            else:
                if self.actualBadge is not None:
                    self.transitState = TransitState.GRANT_REQ_BADGEPLATE
                else:
                    self.transitState = TransitState.WAIT_FOR_BADGE
        # wait for policy
        if self.transitState == TransitState.WAIT_FOR_POLICY_BADGE:
            
            if event.eventType == EventType.ONLY_BADGE_POLICY and event.value.strip(",")[0] == self.actualBadge:
                # grant ok
                self.transitState = TransitState.GRANT_OK
            else:
                if self.actualPlate is not None:
                    self.transitState = TransitState.GRANT_REQ_BADGEPLATE
                else:
                    self.transitState = TransitState.WAIT_FOR_PLATE
        
        if self.transitState == TransitState.GRANT_REQ_BADGEPLATE:
            # richiesta grant badgeplate
            self.dbRequest(RequestType.FIND_PLATE_BADGE,[self.actualPlate,self.actualBadge,self.startTimeTransit])
            self.transitState = TransitState.GRANT_RES_BADGEPLATE
        
        # risposta badgeplate
        if self.transitState == TransitState.GRANT_RES_BADGEPLATE:
            if event.eventType == EventType.BADGE_PLATE_OK:
                self.transitState = TransitState.GRANT_OK

        #wait for badge
        if self.transitState == TransitState.WAIT_FOR_BADGE:
            self.setActualBadge(event.value)
            self.transitState = TransitState.GRANT_REQ_BADGEPLATE
        # wait for plate
        if self.transitState == TransitState.WAIT_FOR_PLATE:
            self.setActualPlate(event.value)
            self.transitState = TransitState.GRANT_REQ_BADGEPLATE
        
        if self.transitState == TransitState.GRANT_OK:
            # connessione alla sbarra
            asyncio.create_task(self.connectToBar())
            # end transit
            self.transitState = TransitState.END_TRANSIT
        
        if self.transitState == TransitState.END_TRANSIT:
            self.endTimeTransit = datetime.now()
            # inserimento transit history
            args = [self.actualPlate,self.actualBadge,self.endTimeTransit]
            self.dbRequest(RequestType.INSERT_TRANSIT_HISTORY,args)
            self.cleanAnalyzer()

    def cleanAnalyzer(self):
        self.actualPlate = None
        self.actualBadge = None
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.startTimeTransit = None
        self.endTimeTransit = None