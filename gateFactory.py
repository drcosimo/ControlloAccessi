from classes import *
from DatabaseSubject import DatabaseSubject
from enums import *
class GateFactory:
    def createGateNord() -> Gate:
        gate = Gate(1,GateName.GATE_NORD)
        gate.loggingMode = False

        lane1 = Lane(1,gate)
        frontCam_L1 = FrontCam("127.0.0.1",10001,lane1)
        rearCam_L1 = RearCam("127.0.0.1",10002,lane1)
        rfid_L1 = Rfid("127.0.0.1",10003,lane1)
        button_L1 = Button("127.0.0.1",10004,lane1)
        db_L1 = DatabaseSubject("127.0.0.1",10006,lane1)
        # connessioni del lane analyzer
        conn_L1 = Connection("127.0.0.1",10006,"127.0.0.1",10005)
        
        lane1.appendDevice(frontCam_L1)
        lane1.appendDevice(rearCam_L1)
        lane1.appendDevice(rfid_L1)
        lane1.appendDevice(db_L1)
        lane1.appendDevice(button_L1)

        lane1.analyzerConnection = conn_L1
        
        gate.appendLane(lane1)
        
        lane2 = Lane(2,gate)
        frontCam_L2 = FrontCam("127.0.0.1",20001,lane2)
        rearCam_L2 = RearCam("127.0.0.1",20002,lane2)
        rfid_L2 = Rfid("127.0.0.1",20003,lane2)
        button_L2 = Button("127.0.0.1",20004,lane2)
        db_L2 = DatabaseSubject("127.0.0.1",20006,lane2)
        # connessioni del lane analyzer
        conn_L2 = Connection("127.0.0.1",20006,"127.0.0.1",20005)
        
        lane2.appendDevice(frontCam_L2)
        lane2.appendDevice(rearCam_L2)
        lane2.appendDevice(rfid_L2)
        lane2.appendDevice(db_L2)
        lane2.appendDevice(button_L2)

        lane2.analyzerConnection = conn_L2
        
        
        gate.appendLane(lane2)

        return gate