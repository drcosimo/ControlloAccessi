from utils.enums import *
from model.Gate import Gate

class Lane():

    def __init__(self,idLane,gate:Gate) -> None:
        self.devices = []
        self.idLane = idLane
        self.gate = gate
        self.laneStatus = LaneStatus.LANE_ACTIVE
        self.analyzerConnection = None

    def appendDevice(self,device):
        self.devices.append(device)

    def activateLane(self):
        self.laneStatus = LaneStatus.LANE_ACTIVE
    
    def deactivateLane(self):
        self.laneStatus = LaneStatus.LANE_NOT_ACTIVE

    def getLaneStatus(self) -> LaneStatus:
        return self.laneStatus

    def getDevices(self):
        return self.devices