from utils.enums import *
from model.Lane import Lane
from reactivex import Observable

class TCPDevice():
    def __init__(self,ip,port,eventType:EventType,deviceType:DeviceType,lane:Lane) -> None:
        self.ip = ip
        self.port = port
        self.eventType = eventType
        self.deviceType = deviceType
        self.lane = lane
    
    def createObservable(self) -> Observable:
        pass