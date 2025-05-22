import 'dart:typed_data';

class EventTypes {
  // Event Types
  static const int EVTTYPE_ALL_SEARCH_NONE_RSP = 0;
  static const int EVTTYPE_GENERAL = 1;
  static const int EVTTYPE_ACTION = 2;
  static const int EVTTYPE_RESTART = 3;
  static const int EVTTYPE_NETWORK_ADDRESS = 4;
  static const int EVTTYPE_ACCESS = 5;
  static const int EVTTYPE_ZONE = 6;
  static const int EVTTYPE_AREA = 7;
  static const int EVTTYPE_INPUT = 8;
  static const int EVTTYPE_OUTPUT = 9;
  static const int EVTTYPE_SUPERVISED_INPUT = 10;
  static const int EVTTYPE_SUPERVISED_OUTPUT = 11;
  static const int EVTTYPE_ZONE_INPUT = 12;
  static const int EVTTYPE_SUPERVISORY = 13;
  static const int EVTTYPE_GENERAL_EQUIPMENT = 14;
  static const int EVTTYPE_EXT_ZONE = 15;
  static const int EVTTYPE_ZONE_EQUIPMENT = 16;
  static const int EVTTYPE_AREA_EQUIPMENT = 17;
  static const int EVTTYPE_EXT_ZONE_EQUIPMENT = 18;
  static const int EVTTYPE_TIMER_ALARM = 19;
  static const int EVTTYPE_SERVICE_DUE = 20;
  static const int EVTTYPE_SUPPLY = 21;
  static const int EVTTYPE_NETWORK = 22;

  // Frame markers
  static const int FRAME_SOT = 0xFE;
  static const int FRAME_EOT = 0xFD;

  // Frame sizes
  static const int FRAME_HEADER_SIZE = 7;
  static const int FRAME_OTHER_FIELD_SIZE = 9;
  static const int FRAME_PAYLOAD_SIZE = 200;
  static const int COMM_EACH_FRAME_SIZE = FRAME_OTHER_FIELD_SIZE + FRAME_HEADER_SIZE + FRAME_PAYLOAD_SIZE;

  // Packet types
  static const int POLL_PKT = 0;
  static const int NRM_PKT = 1;
  static const int ACK_PKT = 2;
  static const int NACK_PKT = 3;
  static const int NWK_PKT = 4;
  static const int SYNC_PKT = 5;
  static const int ACCESS_KEY_PKT = 6;
  static const int DUMMY_PKT = 7;
  static const int EVT_LOG_PKT = 8;

  // Request modes
  static const int POLL_REQ_MODE = 0;
  static const int MODULE_REQ_MODE = 1;
  static const int DB_SETUP_REQ_MODE = 2;
  static const int DB_STATUS_REQ_MODE = 3;
  static const int CNTRL_REQ_MODE = 4;
  static const int EVT_LOG_RSP = 5;

  // Instruction modes
  static const int POLL_INSTRUCT_MODE = 0x80;
  static const int MODULE_INSTRUCT_MODE = 0x81;
  static const int DB_SETUP_INSTRUCT_MODE = 0x82;
  static const int DB_STATUS_INSTRUCT_MODE = 0x83;
  static const int CNTRL_INSTRUCT_MODE = 0x84;

  // Socket types
  static const int SOCKET_PANEL = 0;
  static const int SOLAR_SETUP = 1;
  static const int SOLAR_EMULATION = 2;
  static const int SOCKET_SERVER = 3;

  // Commands
  static const int EVENT_STATUS_CMD = 0x02;
  static const int EVT_LOG_CMD = 0x03;

  // Panel states
  static const int PANEL_NOT_CONNECTED = 0;
  static const int PANEL_CONNECTED = 1;
  static const int PANEL_PROCESS = 2;

  // Process states
  static const int REQ_NWK_PKT = 0;
  static const int REQ_ACCESS_KEY = 1;
  static const int DUMMYPKT_SEND = 2;
  static const int READ_EVT_LOG = 3;
  static const int REQ_RSP_WAIT_STATE = 4;

  // Frame details
  static const int SCRIPT_ORIG = 0;
  static const int SCRIPT_DEST = 1;

  // Event log details
  static const int LOG_NW = 0;  // network
  static const int LOG_ND = 0;  // Node
  static const int LOG_SND = 0; // Sub node
  static const int LOG_MO = 0;  // Module
  static const int LOG_MD = 2;  // Mode
  static const int LOG_SK = 0;  // Socket
  static const int LOG_CMD = 2; // cmd

  // Event log search parameters
  static const int LOG_EVT_SEARCH_METHOD = 0x04;  // 1 byte
  static const int LOG_EVT_SEARCH_NUMBER = 0x000003E8;  // 1000th log number

  static Map<int, String> supervisoryFaultParam12Name = {
    2: "Open",
    3: "Short",
    4: "Double EOL",
    5: "Low resistance",
    7: "Overload"
  };

  static Map<int, String> eventParam0NumberNameList = {
    6: "Zone no.{par0}",
    10: "Input no.{par0}",
    11: "Output no.{par0}",
    12: "Input no.{par0}",
    15: "Ext. zone no.{par0}",
  };

  static Map<int, String> eventParam1NumberNameList = {
    16: "Zone no.{par1}",
    17: "Area no.{par1}",
    18: "Ext zone no.{par1}",
  };
} 