from time import strftime
from reactivex import Observer
from model.Event import Event

from datetime import date, datetime

from utils.enums import DeviceType, EventType
class Logger(Observer):

    def __init__(self,lane):
        self.actualPlate = None
        self.actualBadge = None
        self.lane = lane
        data = date.today().strftime('%d-%m-%Y')
        self.fileName = "../loggingFiles/log_{0}_{1}.txt".format(lane.idLane,data)

    def checkDate(self):
        today = date.today().strftime('%d-%m-%Y')
        fileDate = self.fileName.split("_")[2]
        if today != fileDate:
            self.fileName = "../loggingFiles/log_{0}_{1}.txt".format(self.lane.idLane,today)
        
    def on_next(self,evento:Event):
        
        # un file per ogni giorno
        self.checkDate()

        # apertura file per scrittura
        with open(file = self.fileName,mode='a') as file:
            if (evento.eventType != EventType.NEED_BADGE and evento.eventType != EventType.NEED_PLATE) and not((evento.eventType == EventType.PLATE or evento.eventType == EventType.BADGE) and (self.actualBadge is not None or self.actualPlate is not None)):
                file.write(f"{datetime.now().strftime('%H:%M:%S')} -[INFO]- \t\t{self.formatEvent(evento)}\n")


    def on_completed(self) -> None:
        return super().on_completed()
    
    def on_error(self, error: Exception) -> None:
        return super().on_error(error)
    
    def formatEvent(self,evt: Event):
        
        value = self.formatEventValue(evt.value)

        evtType = int(evt.eventType)
        devType = int(evt.deviceType)

        if self.actualPlate is None and self.actualBadge is None:
            if evtType == EventType.PLATE:
                self.actualPlate = evt.value
                return f"TRANSIT_STARTED_FROM_PLATE\t{value}\t READ BY {DeviceType(devType).name}" 
            elif evtType == EventType.BADGE:
                self.actualBadge = evt.value
                return f"TRANSIT_STARTED_FROM_BADGE\t{value}\t READ BY {DeviceType(devType).name}"
        
        if evtType == EventType.HUMAN_ACTION:
            self.cleanLogger()
            return "manual_open_gate"

        if evtType == EventType.GRANT_REFUSED:
            self.cleanLogger()
            return f"ACCESS_REFUSED TO\t{value}"
        
        if evtType == EventType.GRANT_OK:
            self.cleanLogger()
            return f"ACCESS_GRANTED TO\t{value}"

        if evtType == EventType.TIMED_OUT:
            self.cleanLogger()
            return f"REQUEST TIMED OUT FOR\t{value}"

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