from time import strftime
from reactivex import Observer
from classes import Event

import logging
from datetime import date

from enums import DeviceType, EventType
class Logger(Observer):

    def __init__(self):
        data = date.today().strftime('%d-%m-%Y')
        self.fileName = "log_{0}".format(data)
        self.configLog()
        logging.getLogger().addHandler(logging.StreamHandler())

    def configLog(self):
        logging.basicConfig(filename=self.fileName,filemode='a',
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%d-%m-%Y %H:%M:%S'
        )

    '''
    tipoevento      targa       badge            device      timestamp
    PLATE           ER232EW      fbasbfabf              FRONTCAM    12.12.12:3
    '''
    #TODO aggiungere formattatore eventi

    def on_next(self,evento:Event):
        # stampa eventi
        # impostazione file giornaliero
        fileDate = self.fileName.split("_")[1]
        actualDate = date.today().strftime('%d-%m-%Y')
        if fileDate != actualDate:
            self.fileName = "log_{0}".format(actualDate)
            self.configLog(self)
        
        logging.info(self.formatEvent(evento))


    def on_completed(self) -> None:
        return super().on_completed()
    
    def on_error(self, error: Exception) -> None:
        return super().on_error(error)
    
    def formatEvent(self,evt:Event):
        if evt is None:
            return f"TRANSIT_ENDED"
        elif evt.eventType == EventType.PLATE or evt.eventType == EventType.BADGE:
            return f"TRANSIT_STARTED_FROM_{EventType(evt.eventType).name}\t{evt.value}\t READ BY{DeviceType(evt.deviceType).name}"
        elif evt.eventType == EventType.HUMAN_ACTION:
            return f"manual_open_gate"
        elif evt.eventType == EventType.NO_POLICY or evt.eventType == EventType.NO_GRANT:
            return f"ACCESS_REFUSED TO\t{evt.value}"
        elif evt.eventType == EventType.ONLY_BADGE_POLICY or evt.eventType == EventType.ONLY_PLATE_POLICY or evt.eventType == EventType.BADGE_PLATE_OK:
            return f"ACCESS_GRANTED TO\t{evt.value}"