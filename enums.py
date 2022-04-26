from enum import Enum

class GateName(Enum):
    GATE_NORD = 1
    GATE_SUD = 2
    GATE_EST = 3
    GATE_OVEST = 4

class EventType(Enum):
    ONLY_BADGE_POLICY = 1
    ONLY_PLATE_POLICY = 2
    BADGE_PLATE_POLICY = 3
    NO_POLICY = 4
    PLATE = 5
    BADGE = 6
    HUMAN_ACTION = 7
    OPEN_GATE = 8
    BADGE_PLATE_OK = 8
    BADGE_OK = 9
    PLATE_OK = 10
    NO_GRANT = 11

class TransitState(Enum):
    WAIT_FOR_TRANSIT = 1
    TRANSIT_STARTED = 2
    GRANT_REQ = 3
    END_TRANSIT = 4
    GRANT_OK = 5
    MANUAL_GRANT_OK = 6
    GRANT_RES_BADGEPLATE = 7
    GRANT_REQ_BADGEPLATE = 8
    WAIT_FOR_RESPONSE = 9
    WAIT_FOR_DATA = 10
    GRANT_REFUSED = 11

class DeviceType(Enum):
    FRONT_CAM = 1
    REAR_CAM = 2
    RFID = 3
    BUTTON = 4
    SERVER = 5
    BAR = 6

class RequestType(Enum):
    POLICY = 1
    FIND_PLATE = 2
    FIND_BADGE = 3
    FIND_PLATE_BADGE = 4
    INSERT_TRANSIT_HISTORY = 5

class LaneStatus(Enum):
    LANE_ACTIVE = 1
    LANE_NOT_ACTIVE = 2