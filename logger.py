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
        
        logging.info(self.formatEvent(evento))


    def on_completed(self) -> None:
        return super().on_completed()
    
    def on_error(self, error: Exception) -> None:
        return super().on_error(error)
    
    def formatEvent(self,evt: Event):
        
        value = self.formatEventValue(evt.value)

        evtType = int(evt.eventType)
        devType = int(evt.deviceType)

        if (evtType == EventType.PLATE and (devType == DeviceType.FRONT_CAM or devType == DeviceType.REAR_CAM)) or (evtType == EventType.BADGE and devType == DeviceType.RFID):
            return f"TRANSIT_STARTED_FROM_{EventType(evtType).name}\t{value}\t READ BY {DeviceType(devType).name}"
        if evtType == EventType.HUMAN_ACTION:
            return "manual_open_gate"
        if evtType == EventType.NO_POLICY or evtType == EventType.NO_GRANT:
            return f"ACCESS_REFUSED TO\t{value}"
        if evtType == EventType.ONLY_BADGE_POLICY or evtType == EventType.ONLY_PLATE_POLICY or evtType == EventType.BADGE_PLATE_OK:
            return f"ACCESS_GRANTED TO\t{value}"


    def formatEventValue(self, evt):
        if evt is not None:
            values = evt.split(",")

            if values[0] == "None" and len(values) > 1:
                return values[1]
            elif len(values) > 1 and values[1] == "None":
                return values[0]
        
            return values

        return None