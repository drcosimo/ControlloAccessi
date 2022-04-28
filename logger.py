from time import strftime
from reactivex import Observer
from classes import Event

import logging
from datetime import date
class Logger(Observer):

    def __init__(self):
        data = date.today().strftime('%d-%m-%Y')
        self.fileName = "log_{0}".format(data)
        self.configLog()
        logging.getLogger().addHandler(logging.StreamHandler())

    def configLog(self):
        logging.basicConfig(filename=self.fileName,filemode='w',
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
        plate,badge,time = evento.value.split(",")
        logging.info(f"{evento.eventType}\t{plate}\t{badge}\t{evento.deviceType}")


    def on_completed(self) -> None:
        return super().on_completed()
    
    def on_error(self, error: Exception) -> None:
        return super().on_error(error)