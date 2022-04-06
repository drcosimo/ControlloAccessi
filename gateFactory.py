from classes import *
from enums import *
class GateFactory:
    def createGateNord() -> Gate:
        gate = Gate(1,GateName.GATE_NORD)
        
        lane1 = Lane(1,gate)
        frontCam_L1 = FrontCam("127.0.0.1",10001,lane1)
        rearCam_L1 = RearCam("127.0.0.1",10002,lane1)
        #rfid_L1 = Rfid("127.0.0.1",10003,lane1)
        #button_L1 = Button("127.0.0.1",10004,lane1)
        lane1.appendDevice(frontCam_L1)
        lane1.appendDevice(rearCam_L1)
        lane2 = Lane(1,gate)
        frontCam_L2 = FrontCam("127.0.0.1",10005,lane2)
        rearCam_L2 = RearCam("127.0.0.1",10006,lane2)
        rfid_L2 = Rfid("127.0.0.1",10007,lane2)
        button_L2 = Button("127.0.0.1",10008,lane2)
        lane1.appendDevice(frontCam_L2)
        lane1.appendDevice(rearCam_L2)
        
        gate.appendLane(lane1)
        gate.appendLane(lane2)
        
        return gate