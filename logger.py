from time import strftime
from reactivex import Observer
from classes import Event

import logging
from datetime import date

from enums import DeviceType, EventType
class Logger(Observer):

    def __init__(self,lane):
        self.actualPlate = None
        self.actualBadge = None
        self.lane = lane
        data = date.today().strftime('%d-%m-%Y')
        self.fileName = "log_{0}_{1}".format(lane.idLane,data)
        self.configLog()
        # logging.getLogger().addHandler(logging.StreamHandler())

    def configLog(self):
        print(f"filename: {self.fileName}")
        logging.basicConfig(filename=self.fileName,filemode='a',
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%d-%m-%Y %H:%M:%S'
        )


    def on_next(self,evento:Event):
        # stampa eventi
        # impostazione file giornaliero
        fileLane = self.fileName.split("_")[1]
        fileDate = self.fileName.split("_")[2]
        actualDate = date.today().strftime('%d-%m-%Y')
        if fileDate != actualDate or self.lane.idLane != fileLane:
            self.fileName = "log_{0}_{1}.txt".format(self.lane.idLane, actualDate)
            self.configLog()

        #print(f"{self.formatEvent(evento)}\t LANE: {evento.lane.idLane}")
        if (evento.eventType != EventType.NEED_BADGE and evento.eventType != EventType.NEED_PLATE) and not((evento.eventType == EventType.PLATE or evento.eventType == EventType.BADGE) and (self.actualBadge is not None or self.actualPlate is not None)):
            logging.info(f"{self.formatEvent(evento)}\t LANE: {evento.lane.idLane}")


    def on_completed(self) -> None:
        return super().on_completed()
    
    def on_error(self, error: Exception) -> None:
        return super().on_error(error)
    
    def formatEvent(self,evt: Event):
        
        value = self.formatEventValue(evt.value)

        evtType = int(evt.eventType)
        devType = int(evt.deviceType)

        # TRANSIT STARTED LOG
        if self.actualPlate is None and self.actualBadge is None:
            if evtType == EventType.PLATE:
                self.actualPlate = evt.value
                return '\033[94m' + f"TRANSIT_STARTED_FROM_PLATE\t{value}\t READ BY {DeviceType(devType).name}" + '\033[0m'
            elif evtType == EventType.BADGE:
                self.actualBadge = evt.value
                return '\033[94m' + f"TRANSIT_STARTED_FROM_BADGE\t{value}\t READ BY {DeviceType(devType).name}" + '\033[0m'
        
        if evtType == EventType.HUMAN_ACTION:
            self.cleanLogger()
            return '\033[96m' + "manual_open_gate" + '\033[0m'

        if evtType == EventType.GRANT_REFUSED:
            self.cleanLogger()
            return '\033[91m' + f"ACCESS_REFUSED TO\t{value}" + '\033[0m'
        
        if evtType == EventType.GRANT_OK:
            self.cleanLogger()
            return '\033[92m' + f"ACCESS_GRANTED TO\t{value}" + '\033[0m'

        return f"evento sbagliato: {evt.toString()}"

    def formatEventValue(self, evt):
        if evt is not None:
            values = evt.split(",")

            if values[0] == "None" and len(values) > 1:
                return values[1]
            elif len(values) > 1 and values[1] == "None":
                return values[0]
        
            return values

        return None

    def cleanLogger(self):
        self.actualBadge = None
        self.actualPlate = None