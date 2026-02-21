# =========================================================
# File: custom_components/lpr_gatebox/const.py
# Project: LPR GateBox HA integration
# Version: 0.1.0
# =========================================================

DOMAIN = "lpr_gatebox"

CONF_BASE_URL = "base_url"
CONF_INCLUDE_DEBUG = "include_debug"
CONF_HEARTBEAT_SEC = "heartbeat_sec"
CONF_POLL_MS = "poll_ms"

DEFAULT_INCLUDE_DEBUG = False
DEFAULT_HEARTBEAT_SEC = 15
DEFAULT_POLL_MS = 250

PLATFORMS = ["sensor", "binary_sensor", "camera"]

# entity keys
SENSOR_LAST_PLATE = "last_plate"
SENSOR_LAST_CONF = "last_confidence"
SENSOR_LAST_STATUS = "last_status"
SENSOR_LAST_MESSAGE = "last_message"
SENSOR_LAST_TS = "last_ts"

BINARY_RTSP_ALIVE = "rtsp_alive"

CAMERA_LIVE_FRAME = "live_frame"