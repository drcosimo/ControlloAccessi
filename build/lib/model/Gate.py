from utils.enums import *


class Gate():
    
    def __init__(self, idGate, gateName:GateName) -> None:
        self.idGate = idGate
        self.gateName = gateName
        self.executionMode = ExecutionMode.AUTOMATION_LOGGING
        self.lanes = []

    def appendLane(self,lane):
        self.lanes.append(lane)

    def getLanes(self):
        return self.lanes