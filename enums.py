from enum import IntEnum

class GateName(IntEnum):
    GATE_NORD = 1
    GATE_SUD = 2
    GATE_EST = 3
    GATE_OVEST = 4

class EventType(IntEnum):
    PLATE = 1
    BADGE = 2
    HUMAN_ACTION = 3
    OPEN_GATE = 4
    GRANT_OK = 5
    GRANT_REFUSED = 6
    NEED_PLATE = 7
    NEED_BADGE = 8

class PolicyType(IntEnum):
    ONLY_BADGE_POLICY = 1
    ONLY_PLATE_POLICY = 2
    BADGE_PLATE_POLICY = 3
    NO_POLICY = 4
    
class TransitState(IntEnum):
    WAIT_FOR_TRANSIT = 1
    TRANSIT_STARTED = 2
    DB_REQ = 3
    DB_RES = 4
    GRANT_OK = 5
    GRANT_REFUSED = 6
    WAIT_FOR_DATA = 7
    END_TRANSIT = 8


class DeviceType(IntEnum):
    FRONT_CAM = 1
    REAR_CAM = 2
    RFID = 3
    BUTTON = 4
    SERVER = 5
    BAR = 6

class RequestType(IntEnum):
    POLICY = 1
    FIND_PLATE = 2
    FIND_BADGE = 3
    FIND_PLATE_BADGE = 4
    INSERT_TRANSIT_HISTORY = 5

class LaneStatus(IntEnum):
    LANE_ACTIVE = 1
    LANE_NOT_ACTIVE = 2