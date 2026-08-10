from enum import Enum


class SourceType(str, Enum):
    VIDEO_FILE = "VIDEO_FILE"
    WEBCAM = "WEBCAM"
    RTSP = "RTSP"


class CameraStatus(str, Enum):
    CONNECTING = "CONNECTING"
    ONLINE = "ONLINE"
    RECONNECTING = "RECONNECTING"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class ZoneType(str, Enum):
    RESTRICTED = "RESTRICTED"
    LOITERING = "LOITERING"
    LINE_CROSSING = "LINE_CROSSING"


class EventType(str, Enum):
    INTRUSION = "INTRUSION"
    LINE_CROSSING = "LINE_CROSSING"
    LOITERING = "LOITERING"


class SeverityLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"