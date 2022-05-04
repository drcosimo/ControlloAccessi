import asyncio
from datetime import datetime
import sys

import reactivex
from custom_errors import AlreadyInitialized
from reactivex import Observable, Subject

from enums import *
from classes import Connection,Event

class TransitAnalyzer(Subject):
    def __init__(self,connection,lane):
        self.actualPlate = None
        self.actualBadge = None
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.connections = connection
        self.startTimeTransit = None
        self.endTimeTransit = None
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
        if evt.lane.idLane == 1:
            print('\033[94m'+"ANALYZER-{0}--stato:{1}".format(evt.toString(),TransitState(state).name) +'\033[0m')
        else:
            print('\033[92m'+"ANALYZER-{0}--stato:{1}".format(evt.toString(),TransitState(state).name) +'\033[0m')

            
    
    async def analyze(self, event:Event): # TODO: aggiungere il tipo all'event

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
                 # passo al secondo stato
                self.transitState = TransitState.TRANSIT_STARTED
            elif event.eventType == EventType.BADGE and event.value != self.lastBadge:
                self.actualBadge = event.value
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
            # TODO aggiungere timeout
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