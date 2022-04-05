from reactive.Controllo_Accessi.enums import DeviceType, EventType, GateName

class Lane():
    devices = []
    def __init__(self,idLane) -> None:
        self.idLane = idLane

class Gate():
    lanes = []
    def __init__(self, idGate, gateName:GateName) -> None:
        self.idGate = idGate
        self.gateName = gateName

class TCPDevice():
    def __init__(self,ip,port,eventType:EventType,deviceType:DeviceType) -> None:
        self.ip = ip
        self.port = port
        self.eventType = eventType
        self.deviceType = deviceType

class FrontCam(TCPClient):
    def __init__(self, ip, port) -> None:
        super().__init__(ip, port,EventType.READ_VEHICLE_CREDENTIAL,DeviceType.FRONT_CAM)

class RearCam(TCPClient):
    def __init__(self, ip, port) -> None:
        super().__init__(ip, port, EventType.READ_VEHICLE_CREDENTIAL, DeviceType.REAR_CAM)

class Rfid(TCPServer):
    def __init__(self, ip, port) -> None:
        super().__init__(ip, port, EventType.READ_PERSON_CREDENTIAL, DeviceType.RFID)


''' TODO
# implementano i metodi per la creazione della socket e la creazione dell'observable 
class TCPServer(TCPDevice):

class TCPClient(TCPDevice):
'''

''' TODO
# classi observer => Analyzer, Logger
'''

''' TODO
# classe di interfacciamento con il db => tutte le chiamate al db saranno 
# fatte tramite metodi di questa classe 
'''