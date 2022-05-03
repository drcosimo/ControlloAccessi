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
        self.lastPlate = None
        self.lastBadge = None

    def on_next(self, event:Event):
        if event is not None:
            asyncio.wait_for(self.analyze(event),60)
        else:
            raise TypeError("L'evento passato risulta NULL")


    def on_error(self, error):
        print(f"E' stato rilevato un errore: {error}")    # TODO: Gestire tramite console oppure tramite logger?


    def on_completed(self):
        print("Evento completato")    # TODO: Gestire tramite console oppure tramite logger?

    
    async def analyze(self, event:Event): # TODO: aggiungere il tipo all'event

        # ----------------------------------------------------
        # waiting for transit q0
        # ----------------------------------------------------
        if self.transitState == TransitState.WAIT_FOR_TRANSIT:
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
            if event.eventType == EventType.HUMAN_ACTION:
                self.transitState = TransitState.GRANT_OK
            else:
                # salvo anche il badge se è arrivato
                if event.eventType == EventType.BADGE and self.actualPlate != None:
                    self.actualBadge = event.value
                # salvo anche la plate se è arrivata
                elif event.eventType == EventType.PLATE and self.actualBadge != None:
                    self.actualPlate = event.value
                # richiesta al db
                self.connections.dbRequest([self.actualPlate,self.actualBadge,self.startTimeTransit])
                self.transitState = TransitState.DB_RES
        
        # ----------------------------------------------------
        # wait for response q3
        # ----------------------------------------------------
       
        if self.transitState == TransitState.DB_RES:
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
            # connessione alla sbarra
            await self.connections.connectToBar()
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
            self.cleanAnalyzer()

    def cleanAnalyzer(self):
        self.lastPlate = self.actualPlate
        self.lastBadge = self.actualBadge
        self.actualBadge = None
        self.actualPlate = None
        self.transitState = TransitState.WAIT_FOR_TRANSIT
        self.startTimeTransit = None
        self.endTimeTransit = None