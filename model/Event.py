from utils.enums import *
import string

class Event():
    def __init__(self,value,eventType,deviceType,lane) -> None:
        self.value = value
        self.deviceType = deviceType
        self.eventType = eventType
        self.lane = lane

    def toString(self) -> string:
        return "VALUE: {0}, EVENT: {1}, DEVICE: {2}, LANE: {3}".format(self.value,EventType(self.eventType).name,DeviceType(self.deviceType).name,self.lane.idLane)
