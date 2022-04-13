from enum import Enum

class GateName(Enum):
    GATE_NORD = 1
    GATE_SUD = 2
    GATE_EST = 3
    GATE_OVEST = 4

class EventType(Enum):
    PLATE = 1
    BADGE = 2
    HUMAN_ACTION = 3
    NO_POLICY = 4
    ONLY_BADGE_POLICY = 5
    ONLY_PLATE_POLICY = 6
    BADGE_PLATE_POLICY = 7
    BADGE_PLATE_OK = 8
    BADGE_OK = 9
    PLATE_OK = 10
    NO_GRANT = 11

class TransitState(Enum):
    WAIT_FOR_TRANSIT = 1
    TRANSIT_STARTED_PLATE = 2
    TRANSIT_STARTED_BADGE = 3
    GRANT_REQ_PLATE = 4
    GRANT_REQ_BADGE = 5
    END_TRANSIT = 6
    GRANT_OK = 7
    WAIT_FOR_BADGE = 8
    WAIT_FOR_PLATE = 9
    MANUAL_GRANT_OK = 10
    GRANT_REQ_BADGEPLATE = 11

class DeviceType(Enum):
    FRONT_CAM = 1
    REAR_CAM = 2
    RFID = 3
    BUTTON = 4
    SERVER = 5

class LaneStatus(Enum):
    LANE_ACTIVE = 1
    LANE_NOT_ACTIVE = 2