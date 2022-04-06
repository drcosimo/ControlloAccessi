from enum import Enum

class GateName(Enum):
    GATE_NORD = 1
    GATE_SUD = 2
    GATE_EST = 3
    GATE_OVEST = 4

class EventType(Enum):
    READ_PERSON_CREDENTIAL=1
    READ_VEHICLE_CREDENTIAL=2
    HUMAN_ACTION=3
    START_TRANSIT_WITH_FRONT_PLATE=4
    START_TRANSIT_WITH_REAR_PLATE=5
    START_TRANSIT_WITH_BADGE=6
    END_TRANSIT=7
    GRANT_REQUEST=8
    GRANT_OK=9

class DeviceType(Enum):
    FRONT_CAM = 1
    REAR_CAM = 2
    RFID = 3
    BUTTON = 4

class LaneStatus(Enum):
    LANE_ACTIVE = 1
    LANE_NOT_ACTIVE = 2