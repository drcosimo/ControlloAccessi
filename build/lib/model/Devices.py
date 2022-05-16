from utils.enums import *
from model.TCPClient import TCPClient
from model.TCPServer import TCPServer
from model.Lane import Lane


class FrontCam(TCPServer):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port,EventType.PLATE,DeviceType.FRONT_CAM,lane)

class RearCam(TCPServer):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port, EventType.PLATE, DeviceType.REAR_CAM,lane)

class Rfid(TCPClient):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port, EventType.BADGE, DeviceType.RFID,lane)

class Button(TCPServer):
    def __init__(self, ip, port,lane:Lane) -> None:
        super().__init__(ip, port, EventType.HUMAN_ACTION, DeviceType.BUTTON,lane)

class Bar(TCPClient):
    def __init__(self, ip, port, eventType: EventType, deviceType: DeviceType, lane: Lane) -> None:
        super().__init__(ip, port, EventType.OPEN_GATE, DeviceType.BAR, lane)
