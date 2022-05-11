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
    TIMED_OUT = 9

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
    REQUEST_TIMED_OUT = 9


class DeviceType(IntEnum):
    FRONT_CAM = 1
    REAR_CAM = 2
    RFID = 3
    BUTTON = 4
    SERVER = 5
    BAR = 6
    ANALYZER = 7

class LaneStatus(IntEnum):
    LANE_ACTIVE = 1
    LANE_NOT_ACTIVE = 2

class ExecutionMode(IntEnum):
    LOGGING = 1
    AUTOMATION = 2
    AUTOMATION_LOGGING = 3