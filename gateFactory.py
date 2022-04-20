from classes import *
from DatabaseSubject import DatabaseSubject
from enums import *
class GateFactory:
    def createGateNord() -> Gate:
        gate = Gate(1,GateName.GATE_NORD)
        
        lane1 = Lane(1,gate)
        frontCam_L1 = FrontCam("127.0.0.1",10001,lane1)
        rearCam_L1 = RearCam("127.0.0.1",10002,lane1)
        rfid_L1 = Rfid("127.0.0.1",10003,lane1)
        button_L1 = Button("127.0.0.1",10004,lane1)
        conn_L1 = DatabaseSubject("127.0.0.1",10005,lane1)
        
        lane1.appendDevice(frontCam_L1)
        lane1.appendDevice(rearCam_L1)
        lane1.appendDevice(rfid_L1)
        lane1.appendDevice(conn_L1)
        lane1.appendDevice(button_L1)
        
        gate.appendLane(lane1)
        
        return gate