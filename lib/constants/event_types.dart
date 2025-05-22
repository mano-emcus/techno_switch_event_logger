class EventTypes {
  // Frame markers
  static const int FRAME_SOT = 0xFE;
  static const int FRAME_EOT = 0xFD;

  // Packet types
  static const int NRM_PKT = 0x01;
  static const int ACK_PKT = 0x02;
  static const int NACK_PKT = 0x03;
  static const int NWK_PKT = 0x04;

  // Process states
  static const int REQ_NWK_PKT = 0;
  static const int REQ_ACCESS_KEY = 1;
  static const int DUMMYPKT_SEND = 2;
  static const int READ_EVT_LOG = 3;
  static const int REQ_RSP_WAIT_STATE = 4;

  // Panel states
  static const int PANEL_NOT_CONNECTED = 0;
  static const int PANEL_CONNECTED = 1;
  static const int PANEL_PROCESS = 2;

  // Modes
  static const int DB_STATUS_INSTRUCT_MODE = 0x83;
  static const int DB_SETUP_REQ_MODE = 0x02;
  static const int EVT_LOG_RSP = 0x02;  // Same as DB_SETUP_REQ_MODE for event log responses

  // Commands
  static const int EVENT_STATUS_CMD = 0x02;

  // Event classes
  static const int EVENT_CLASS_SYSTEM = 1;
  static const int EVENT_CLASS_ACTION = 2;
  static const int EVENT_CLASS_ALARM = 3;
  static const int EVENT_CLASS_STATUS = 4;
  static const int EVENT_CLASS_DIAGNOSTIC = 5;
  static const int EVENT_CLASS_NETWORK = 6;

  // Event status
  static const int EVENT_STATUS_ACTIVE = 0;
  static const int EVENT_STATUS_CLEARED = 1;
  static const int EVENT_STATUS_LOGGED = 2;

  // Event types
  static const int EVENT_TYPE_NETWORK_COMM_DOWN = 0x01;
  static const int EVENT_TYPE_NETWORK_COMM_UP = 0x02;
  static const int EVENT_TYPE_NETWORK_ADDRESS = 0x03;
  static const int EVENT_TYPE_NETWORK_CONFIG = 0x04;
  static const int EVENT_TYPE_NETWORK_STATUS = 0x05;

  // Frame sizes
  static const int COMM_EACH_FRAME_SIZE = 216;

  // Search methods
  static const int LOG_EVT_SEARCH_METHOD = 0x04;
  static const int LOG_EVT_SEARCH_NUMBER = 0x3E7;

  // Network parameters
  static const int SCRIPT_DEST = 0x01;
  static const int SCRIPT_ORIG = 0x00;
  static const int LOG_NW = 0x00;
  static const int LOG_ND = 0x00;
  static const int LOG_SND = 0x00;
  static const int LOG_MO = 0x00;
  static const int LOG_MD = 0x02;
  static const int LOG_SK = 0x00;
  static const int LOG_CMD = 0x02;
} 