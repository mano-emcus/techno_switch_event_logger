import serial
import serial.tools.list_ports
import threading
import time
import signal
import sys
import binascii
import datetime

import timestampconverter as tsconverter

# Globals
    

# Creating a 2D list to map STATUS_EVENT_TYPE and STATUS_EVENT_SUB_TYPE to descriptions
# Based on the tables in the images provided.

#List of event type
EVTTYPE_ALL_SEARCH_NONE_RSP       = 0
EVTTYPE_GENERAL                   = 1
EVTTYPE_ACTION                    = 2
EVTTYPE_RESTART                   = 3
EVTTYPE_NETWORK_ADDRESS           = 4
EVTTYPE_ACCESS                    = 5
EVTTYPE_ZONE                      = 6
EVTTYPE_AREA                      = 7
EVTTYPE_INPUT                     = 8
EVTTYPE_OUTPUT                    = 9
EVTTYPE_SUPERVISED_INPUT          = 10
EVTTYPE_SUPERVISED_OUTPUT         = 11
EVTTYPE_ZONE_INPUT                = 12
EVTTYPE_SUPERVISORY               = 13
EVTTYPE_GENERAL_EQUIPMENT         = 14
EVTTYPE_EXT_ZONE                  = 15
EVTTYPE_ZONE_EQUIPMENT            = 16
EVTTYPE_AREA_EQUIPMENT            = 17
EVTTYPE_EXT_ZONE_EQUIPMENT        = 18
EVTTYPE_TIMER_ALARM               = 19
EVTTYPE_SERVICE_DUE               = 20
EVTTYPE_SUPPLY                    = 21
EVTTYPE_NETWORK                   = 22


supervisoryfault_param1_2_name={
    2:"Open",           
    3:"Short",
    4:"Double EOL",
    5:"Low resistance",
    7:"Overload"
}

event_param0_number_name_list={
    #Param0         
    6 :"Zone no.{par0}",#6
    10:"Input no.{par0}",#10
    11:"Output no.{par0}",#11
    12:"Input no.{par0}",#12
    15:"Ext. zone no.{par0}",#15
}

event_param1_number_name_list={
    16:"Zone no.{par1}",#16
    17:"Area no.{par1}",#17
    18:"Ext zone no.{par1}",#18
}

# value=10
# print(event_param0_number_name_list[10].format(param=value))


STATUS_EVENT_DESCRIPTION_VALUE = [
    # 0-None
    [ [[""],[""],[""] ]], # N/A
    #  1-General 
    [ [[""],[""],[""] ]], # N/A
    #  2-Action 
    [ [[""],[""],[""] ]], # N/A
    # 3 - Restart
    [
        #"Cause"
        #param0                 #param1     #param2     
        [ ["Other"],               [""],         [""] ], #
        [ ["Power-on"],            [""],         [""] ], # 1
        [ ["Brown-out"],           [""],         [""] ], # 2
        [ ["External reset pin"],  [""],         [""] ], # 3
        
        # [ [ ["Other"],               [""],         [""] ] ], # 0
        # [ [ ["Power-on"],            [""],         [""] ] ], # 1
        # [ [ ["Brown-out"],           [""],         [""] ] ], # 2
        # [ [ ["External reset pin"],  [""],         [""] ] ], # 3
        # Watchdog time-out"        # 4
        [ 
            #param1                         #param2       
            [ ["None"                        ] , [ "" ] ] , #0
            [ ["Time-out"                    ] , [ "" ] ] , #1
            [ ["Initialisation fault"        ] , [ "" ] ] , #2
            [ ["Application restart"         ] , [ "" ] ] , #3
            [ ["Communication time-out"      ] , [ "" ] ] , #4
            [ ["Excessive communication NAKs"] , [ "" ] ] , #5
            [ ["Invalid RTOS queue"          ] , [ "" ] ] , #6
            [ ["Invalid RTOS queue depth"    ] , [ "" ] ] , #7
            [ ["Invalid RTOS semaphore"      ] , [ "" ] ] , #8
            [ ["Invalid RTOS process"        ] , [ "" ] ] , # 9
            [ ["Invalid RTOS timer"          ] , [ "" ] ] , #10
            [ ["Invalid RTOS mailbox"        ] , [ "" ] ] , #11
            [ ["Corrupted RTOS mailbox"      ] , [ "" ] ] , #12
            [ ["Flash not ready"             ] , [ "" ] ] , #13
            [ ["Database error"              ] , [ "" ] ] , #14
            [ ["System restart"              ] , [ "" ] ] , #15
            [ ["Invalid network"             ] , [ "" ] ] , #16
            [ ["Invalid network address"     ] , [ "" ] ] , #17
            [ ["Serial SRAM error"           ] , [ "" ] ] , #18
            [ ["Serial FLASH error"          ] , [ "" ] ] , #19
            [ ["Memory copy error"           ] , [ "" ] ] , #20
            [ ["Serial FLASH not ready"      ] , [ "" ] ] , #21
            [ ["Serial SRAM not ready"       ] , [ "" ] ] , #22
            [ ["ADC fault"                   ] , [ "" ] ] , #23
            [ ["INTC unhandled interrupt"    ] , [ "" ] ] , #24
            [ ["SER. FLASH installation"     ] , [ "" ] ] , #25
            [ ["RTC fault"                   ] , [ "" ] ] , #26
            [ ["USB fault"                   ] , [ "" ] ] , #27
        ],
        
        #param0                         #param1     #param2
        [ ["JTAG reset"]                  , [""], ["" ] ] , #5
        [ ["CPU error"]                   , [""], ["" ] ] , #6
        [ ["OCD"]                         , [""], ["" ] ] , #7
        [ ["JTAG hard reset"]             , [""], ["" ] ] , #8
        [ ["Software reset"]              , [""], ["" ] ] , #9
        [ ["Deep software reset"]         , [""], ["" ] ] , #10
        [ ["Voltage monitoring reset 0"]  , [""], ["" ] ] , #11
        [ ["Voltage monitoring reset 1"]  , [""], ["" ] ] , #12
        [ ["Voltage monitoring reset 2"]  , [""], ["" ] ] , #13
        
        # Independent watchdog time-out     # 14
        [    
            #param1                         #param2     
            [ ["None"]                         , ["" ] ] , #0
            [ ["Time-out"]                     , ["" ] ] , #1
            [ ["Initialisation fault"]         , ["" ] ] , #2
            [ ["Application restart"]          , ["" ] ] , #3
            [ ["Communication time-out"]       , ["" ] ] , #4
            [ ["Excessive communication NAKs"] , ["" ] ] , #5
            [ ["Invalid RTOS queue"]           , ["" ] ] , #6
            [ ["Invalid RTOS queue depth"]     , ["" ] ] , #7
            [ ["Invalid RTOS semaphore"]       , ["" ] ] , #8
            [ ["Invalid RTOS process"]         , ["" ] ] , #9
            [ ["Invalid RTOS timer"]           , ["" ] ] , #10
            [ ["Invalid RTOS mailbox"]         , ["" ] ] , #11
            [ ["Corrupted RTOS mailbox"]       , ["" ] ] , #12
            [ ["Flash not ready"]              , ["" ] ] , #13
            [ ["Database error"]               , ["" ] ] , #14
            [ ["System restart"]               , ["" ] ] , #15
            [ ["Invalid network"]              , ["" ] ] , #16
            [ ["Invalid network address"]      , ["" ] ] , #17
            [ ["Serial SRAM error"]            , ["" ] ] , #18
            [ ["Serial FLASH error"]           , ["" ] ] , #19
            [ ["Memory copy error"]            , ["" ] ] , #20
            [ ["Serial FLASH not ready"]       , ["" ] ] , #21
            [ ["Serial SRAM not ready"]        , ["" ] ] , #22

        ],
        
        [["Cold start"],[""],[""]]
    ],
    # 4-Network communication
    [
        #Network and addr
        #param0     #param1     #param2     
        [ ["Modules"]   , [""], ["" ] ] , #0
        [ ["Panels"]    , [""], ["" ] ] , #1
        [ ["Repeaters"] , [""], ["" ] ] , #2
        [ ["Setup"]     , [""], ["" ] ] , #3
        [ ["Server"]    , [""], ["" ] ] , #4
        [ [""]          , [""], ["" ] ] , #5

    ],
    # 5 - Access
    [
        #param0     #param1     #param2     
        [ ["Control"]   , [""], ["" ] ] , #0
        [ ["Keyboard"]  , [""], ["" ] ] , #1
        [ ["Setup"]     , [""], ["" ] ] , #2
        [ ["Server"]    , [""], ["" ] ] , #3

    ],
    
    # 6 - Zone
    [ [["Zone no."],[""],[""] ]], # N/A
    
    # 7 - Area
    [ [["Area no."],[""],[""] ]], # N/A
    
    # 8 - Input
    [ [[""],[""],[""]] ], # N/A
    
    # 9 - Output
    [ [[""],[""],[""] ]], # N/A
    
    # 10 - Input no
    [ [["Input no."],[""],[""] ]], # N/A
    
    # 11 - Output no
    [ [["Output no."],[""],[""] ]], # N/A
    
    # 12 - Zone input
    [ [["Input no."],[""],[""] ]], # N/A
    
    # 13 - Supervisory
    [ [["Supervisory-ID"],[""],[""] ]], # N/A
    
    # 14 - General equipement
    [
        #param0                                       #param1    #param2  
        [ ["Alarm sounder equipment(ASE)"]          , [""]  ,    [""] ],#0
        [ ["Coincident sounder equipment(CSE)"]     , [""]  ,    [""] ],#1
        [ ["External alarm sounder equipment(ESE)"] , [""]  ,    [""] ],#2
        [ ["Supervisory sounder equipment(SSE)"]    , [""]  ,    [""] ],#3
    ],

    # 15 - Ext.Zone
    [ [ ["Ext.zone no."],[""],[""] ] ], # N/A

    # 16 - Zone equipement
    #param0                                       #param1   #param2
    [ [ ["Alarm sounder equipment(ASE)"]          , [""]  ,   [""] ] ],#0
    
    # 17 - Area equipement
    [
        #param0                                       #param1  #param2
        [ ["Alarm sounder equipment(ASE)"]          , [""]  ,  [""] ],#0
        [ ["Coincident sounder equipment(CSE)"]     , [""]  ,  [""] ],#1
    ],

    # 18 - Ext zone equipement
    #param0                                         #param1    #param2
    [
        [ ["Release equipment (ERE)"]                   , [""]  ,  [""] ],#0
        [ ["Release initiated sounder equipment (ISE)"] , [""]  ,  [""] ],#1        
        [ ["Release sounder equipment (RSE)"]           , [""]  ,  [""] ],#2
        [ ["Manual release sounder equipment (MSE)"]    , [""]  ,  [""] ],#3
    ],
    
    # 19 - Time alarm
    #param0                    #param1   #param2
    [ [ ["Time alarm no."]      , [""]  ,   [""] ] ],#0

    # 20 - Service due
    [ [[""],[""],[""] ]], # N/A

    # 21 - Supply
    [ [[""],[""],[""] ]], # N/A

    # 22 - Network communication
    [
        #Network
        #param0     #param1     #param2     
        [ ["Modules"]   , [""], ["" ] ] , #0
        [ ["Panels"]    , [""], ["" ] ] , #1
        [ ["Repeaters"] , [""], ["" ] ] , #2
        [ ["Setup"]     , [""], ["" ] ] , #3
        [ ["Server"]    , [""], ["" ] ] , #4
    ],
    
]  

EVENT_DESCRIPTIONS = [
    # 0 - None
    ["-"],

    # 1 - General
    [
        "Memory lock open",
        "Service switch open",
        "Tamper switch open",
        "Key-lock open",
        "Non-volatile memory changed",
        "Configuration changed",
        "External fault",
        "External alarm 1",
        "Configuration defaulted",
        "Vaux overload",
        "External alarm 2",
        "Evacuation",
        "External Supervisory on",
        "External supply fault",
        "Sounders disabled",
        "Event buffer cleared",
        "Non-volatile text changed",
        "Firmware changed",
        "Firmware check-sum error"
    ],

    # 2 - Action
    [
        "Memory lock closed",
        "Service switch closed",
        "Tamper switch closed",
        "Key-lock closed",
        "Reset",
        "Time changed",
        "Time defaulted",
        "Controls enabled",
        "Controls disabled",
        "Silence buzzer",
        "Silence sounders",
        "Activate sounders",
        "N/A",
        "External fault ok",
        "External controls disabled",
        "Vaux ok",
        "External Supervisory off",
        "External controls enabled",
        "External supply fault ok",
        "Sounders enabled",
        "Sounder delays enabled",
        "Sounder delays disabled",
        "External reset",
        "External silence buzzer",
        "External silence sounders",
        "External activate sounders",
        "I/O suspended",
        "Local Controls enabled",
        "Local Controls disabled"
    ],

    # 3 - Restart
    ["-"],

    # 4 - Network
    [
        "Network communication down",
        "Network communication up",
        "Invalid Product Type",
        "No Permission",
        "Invalid Hardware Version (Major & Minor)",
        "Invalid Product Option",
        "Invalid Product Version",
        "Invalid Software Build",
        "Invalid Software Version (Major & Minor)",
        "Invalid Software Release",
        "Invalid Software Date",
        "Invalid Software Protocol",
        "Invalid Product Revision",
        "Silence Buzzer",
        "Tamper on",
        "Tamper off",
        "Local controls enabled",
        "Local controls disabled",
        "Double address",
        "Extnl controls enabled",
        "Extnl controls disabled"
    ],

    # 5 - Access
    [
        "Enabled",
        "Violation",
        "Disabled"
    ],

    # 6 - Zone
    [
        "Enabled",
        "Disabled",
        "Test On",
        "Test Off",
        "Alarm (Auto)",
        "Fault",
        "Supervisory fault",#\n(Zone input allocated to zone)
        "Supervisory normal",#\n(Zone input allocated to zone)
        "Test-alarm on",
        "Test-alarm off",
        "Alarm off (Auto)",
        "Alarm (MCP)",
        "Alarm off (MCP)",
        "Evacuation"
    ],
    # 7 - Area
    [
        "Enabled",
        "Disabled",
        "Test On",
        "Test Off",
        "Alarm",
        "Fault",
        "Coincidence",
        "Test-alarm on",
        "Test-alarm off",
        "Test-coincidence on",
        "Test-coincidence off",
        "Evacuation"
    ],

    # 8 - Input
    [
        "Enabled",
        "Disabled",
        "Test On",
        "Test Off",
        "Input on (test)",
        "Input off (test)",
        "Input duplication"
    ],

    # 9 - Output
    [
        "Enabled",
        "Disabled",
        "Test On",
        "Test Off"
    ],

    # 10 - Supervised Input
    [
        "Supervisory fault",#\n(for input without allocation)
        "Supervisory normal"#\n(for input without allocation)
    ],

    # 11 - Supervised Output
    [
        "Supervisory fault",#\n(for output without allocation)
        "Supervisory normal"#\n(for output without allocation)
    ],

    # 12 - Zone Input
    [
        "Supervisory fault",#\n(for input without allocation)
        "Supervisory normal"#\n(for input without allocation)
    ],

    # 13 - Supervisory
    [
        "Process limit",
        "Mailbox limit",
        "Queue limit"
    ],

    # 14 - General Equipment
    [
        "Enabled",
        "Disabled",
        "Test On",
        "Test Off",
        "Fault",
        "Normal",
        "Delay enabled",
        "Delay disabled"
    ],

    # 15 - Ext. Zone
    [
        "Enabled",
        "Disabled",
        "Test On",
        "Test Off",
        "Fault On",
        "Fault Off",
        "Automatic mode",
        "Manual mode",
        "Manual release initiated",
        "Automatic release initiated",
        "Extinguishant released",
        "Release aborted",
        "Hold on",
        "Hold off",
        "Release end",
        "Extinguishing reset blocked",
        "Extinguishing reset allowed",
        "Abort on",
        "Abort off",
        "Pressure monitor low",
        "Pressure monitor normal",
        "Valve monitoring on",
        "Valve monitoring off",
        "Release count down restarted",
        "Release count down suspended",
        "Release count down continued",
        "Release count down terminated",
        "Extinguishant release start",
        "Actuator undefined",
        "Actuator defined",
        "Manual test-release on",
        "Manual test-release off",
        "Automatic test-release on",
        "Automatic test-release off",
        "Timed Extraction start",
        "Timed Extraction end",
        "Manual Extraction start",
        "Manual Extraction end",
        "External gas disable on",
        "External gas disable off",
        "External supervisory on",
        "External supervisory off",
        "MCP alarm",
        "Extn1 MCP alarm",
        "Valve fault on",
        "Valve fault off",
        "Start delayed extraction",
        "External extinguishing fault on",
        "External extinguishing fault off",
        "Hold fault on",
        "Hold fault off",
        "Auto/Manual fault on",
        "Auto/Manual fault off",
        "Hold disabled",
        "Hold enabled",
        "Extnl Manual Trigger Fault on",
        "Extnl Manual Trigger Fault off",
        "Extnl Gas Disable Fault on",
        "Extnl Gas Disable Fault off",
        "Extnl Extinguishing Flt Fault on",
        "Extnl Extinguishing Flt Fault off"
    ],

    # 16 - Zone Equipment
    [
        "Enabled",
        "Disabled",
        "Test On",
        "Test Off",
        "Fault",
        "Normal",
        "Delay enabled",
        "Delay disabled"
    ],

    # 17 - Area Equipment
    [
        "Enabled",
        "Disabled",
        "Test On",
        "Test Off",
        "Fault",
        "Normal",
        "Delay enabled",
        "Delay disabled"
    ],

    # 18 - Ext. Zone Equipment
    [
        "Enabled",
        "Disabled",
        "Test On",
        "Test Off",
        "Fault",
        "Normal",
        "Delay enabled",
        "Delay disabled"
    ],

    # 19 - Timer alarm
    [
        "Alarm on",
        "Alarm off"
    ],

    # 20 - Service due
    [
        "Service due"
    ],
    # 21 - Supply
    [
        "Earth fault ok",         # 0
        "Earth fault high",       # 1
        "Earth fault low",        # 2
        "Vin voltage ok",         # 3
        "Vin voltage high",       # 4
        "Vin voltage low",       # 5 (assuming "ow" is a typo for "low")
        "Vout voltage ok",        # 6
        "Vout voltage high",      # 7
        "Vout voltage low",       # 8
        "Mains ok",               # 9
        "Mains fault",            # 10
        "Battery voltage ok",     # 11
        "Battery voltage high",   # 12
        "Battery voltage low",    # 13
        "Battery low warning",    # 14
        "Battery shut-off",       # 15
        "Battery disconnected",   # 16
        "Battery connected",      # 17
        "Charger fault",          # 18
        "Charger ok",             # 19
        "Booster fault",          # 20
        "Booster ok",             # 21
        "Battery test fault",     # 22
        "Battery test ok",        # 23
        "Supply fault",           # 24
        "Supply fault ok",        # 25
        "Extnl fault",            # 26 (External)
        "Extnl fault ok"          # 27
    ],

     # 22 - Network
    [
        "Ring open",
        "Ring closed",
        "Ring disconnect",
        "Test on",
        "Test off"
    ]

]


STATUS_EVENT_TYPE_DESCRIPTIONS = [
    "All (search), None (response)",   # 0
    "General",                         # 1
    "Action",                          # 2
    "Restart",                         # 3
    "Network Address",                 # 4
    "Access",                          # 5
    "Zone",                            # 6
    "Area",                            # 7
    "Input",                           # 8
    "Output",                          # 9
    "Supervised Input",                # 10
    "Supervised Output",               # 11
    "Zone Input",                      # 12
    "Supervisory",                     # 13
    "General equipment",               # 14
    "Ext. zone",                       # 15
    "Zone equipment",                  # 16
    "Area equipment",                  # 17
    "Ext. zone equipment",             # 18
    "Timer alarm",                     # 19
    "Service due",                     # 20
    "Supply",                          # 21
    "Network"                          # 22
]

STATUS_EVENT_CLASS_NAMES = [
    "All(search),None(Response)",
    "Release",
    "Alarm",
    "Fault",
    "Disablement",
    "Condition",
    "Action",
    "Evacuation",
]

# List of method names as strings (index matches the value)
STATUS_EVENT_SEARCH_METHOD_NAMES = [
    "Highest_priority",
    "Class_highest_priority_incremental",
    "Class_increment",
    "Class_decrement",
    "Search_number",
    "Normal_oldest",
    "Normal_increment",
    "Normal_decrement",
    "Event_number",
    "Dump",
    "Dump_increment",
    "Dump_decrement",
    "First_highest_priority",
    "Class_highest_priority",
    "Non_release_highest_priority",
    "Normal_newest"
]


STATUS_EVENT_STATUS_VALUE = [
"All(search),Passive(Response)",
"Active",
"Accepted",
"Logged"    
]

# 2D list of STATUS_EVENT_SUB_CLASS descriptions by class and subclass
STATUS_EVENT_SUB_CLASS_DESCRIPTIONS = [
    # Class 0: All, None
    ["All (search), None (response)"],
    
    # Class 1: Release
    ["All (search), None (response)", "Manual release", "Automatic release"],
    
    # Class 2: Alarm
    [
        "All (search), None (response)",
        "External alarm",
        "Manual alarm (Extinguishing)",
        "MCP alarm",
        "Automatic alarm",
        "Evacuation alarm"
    ],
    
    # Class 3: Fault
    [
        "All (search), None (response)",
        "System fault",
        "Supply fault",
        "Module communication",
        "Panel communication",
        "Repeater communication",
        "Setup communication",
        "Server communication",
        "Repeater fault",
        "Repeater supply fault"
    ],
    
    # Class 4: Disablement
    ["All (search), None (response)"],
    
    # Class 5: Condition
    [
        "All (search), None (response)",
        "Pre-alarm",
        "Test-Alarm",
        "Test-Condition",
        "Coincidence",
        "Test",
        "Supervisory",
        "Release start",
        "Module communication test",
        "Panel communication test",
        "Repeater communication test",
        "Setup communication test",
        "Server communication test"
    ],
    
    # Class 6: Action
    ["All (search), None (response)"],

     # Class 7: Action
    ["Evacuation"]
]

#header 7 bytes
comm_header = {
    'nwk': 0x00,
    'nod': 0x00,
    'subnod': 0x00,
    'module': 0x00,
    'mode': 0x00,
    'sck': 0x00,
    'cmd': 0x00,
}

#data 7+200->207 bytes
comm_data = {
    'header': comm_header,
    'data': [0x00] * 200  # Always initialize with 200 zeros
}

#total frame data 207+9->216 bytes
comm_frame = {
    'sot': 0x00,
    'dest': 0x00,
    'origin': 0x00,
    'pkt_typ': 0x00,
    'txp': 0x00,
    'rxp': 0x00,
    'payload': comm_data,
    'crc': 0x0000,
    'eot': 0x00,
}

rx_poll_rsp = 0
running = True
ser = None

FRAME_SOT = 0xFE
FRAME_EOT = 0xFD

FRAME_HEADER_SIZE   = 7
FRAME_OTHER_FILED_SIZE   = 9 # Includes ( sot,eot,txp,rxp,pkttyp,crc,orig,des)
FRAME_PAYLOAD_SIZE = 200

#TOTAL SIZE OF EACH PKT IS 216 BYTES WHICH IS HARDCODED
COMM_EACH_FRAME_SIZE    = FRAME_OTHER_FILED_SIZE + FRAME_OTHER_FILED_SIZE + FRAME_PAYLOAD_SIZE

# List of pakcet type
POLL_PKT    = 0
NRM_PKT     = 1
ACK_PKT     = 2
NACK_PKT    = 3
NWK_PKT     = 4
SYNC_PKT    = 5


# Request modes return data from the module.
POLL_REQ_MODE       = 0   
MODULE_REQ_MODE     = 1
DB_SETUP_REQ_MODE   = 2
DB_STATUS_REQ_MODE  = 3
CNTRL_REQ_MODE      = 4

# Instruction mode send data to the module.
POLL_INSTRUCT_MODE       = 0x80   
MODULE_INSTRUCT_MODE     = 0x81
DB_SETUP_INSTRUCT_MODE   = 0x82
DB_STATUS_INSTRUCT_MODE  = 0x83
CNTRL_INSTRUCT_MODE      = 0x84

#List of scoket
SOCKET_PANEL    = 0
SOLAR_SETUP     = 1
SOLAR_EMULATION = 2   
SOCKET_SERVER   = 3

#List of cmds
EVENT_STATUS_CMD = 0x02

#panel communication port state
PANEL_NOT_CONNECTED = 0
PANEL_CONNECTED     = 1
PANEL_PROCESS       = 2

#panel process state
REQ_NWK_PKT         = 0
REQ_ACCESS_KEY      = 1
DUMMYPKT_SEND       = 2    
READ_EVT_LOG        = 3
REQ_RSP_WAIT_STATE  = 4

#Frame details
SCRIPT_ORIG = 0
SCRIPT_DEST = 1

PKTTX_CNT = 0
PKTRX_CNT = 0

# Event log details variable
LOG_NW  = 0 #network
LOG_ND  = 0 #Node
LOG_SND = 0 #Sub node
LOG_MO  = 0 #Module 
LOG_MD  = 2 #Mode
LOG_SK  = 0 #Socket
LOG_CMD = 2 #cmd 

LOG_EVT_SEARCH_METHOD = 0x04        #1byte
LOG_EVT_SERACH_NUMBER = 0x00000000  # 4bytes
LOG_EVT_SERACH_NUMBER = 0x000003E8  # 1000 th log number

main_process_statemachine   = REQ_NWK_PKT
process_state               = REQ_NWK_PKT
panel_connecte_state        = PANEL_NOT_CONNECTED
stop_evt_log_read           = 0

def format_hex_string(hex_str):
    # Ensure even length
    if len(hex_str) % 2 != 0:
        raise ValueError("Hex string must have even length")
    
    formatted = []
    for i in range(0, len(hex_str), 2):
        byte = hex_str[i:i+2]
        formatted.append(f"{byte.lower()}")

    return " ".join(formatted)

def display_msg(msg):
    print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  {msg}  >>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    
def signal_handler(sig, frame):
    global running
    print("\n[INFO] Ctrl+C detected, stopping threads...")
    running = False
    time.sleep(0.3)
    sys.exit(0)


def tools_fletcher_checksum(p_buffer):
    length = len(p_buffer)
    checksum = 0

    if length > 0:
        sum1 = 0
        sum2 = 0
        for i in range(length):
            sum1 = (sum1 + p_buffer[i]) % 255
            sum2 = (sum2 + sum1) % 255

        chk1 = (255 - ((sum1 + sum2) % 255)) & 0xFF
        chk2 = (255 - ((sum1 + chk1) % 255)) & 0xFF

        checksum = (chk1 << 8) | chk2

    return checksum





def parse_and_update_rx_comm_pkt(rx_frame,rx_frame_len):
    global comm_frame
    # print("rx_frame type:",type(rx_frame))
    frame_pkt_bytes = list(rx_frame)

    # frame_pkt_bytes = [int(rx_frame[i:i+2], 16) for i in range(0, len(rx_frame), 2)]
        
    comm_frame['sot']                           = frame_pkt_bytes[0]
    comm_frame['dest']                          = frame_pkt_bytes[1]
    comm_frame['origin']                        = frame_pkt_bytes[2]
    comm_frame['pkt_typ']                       = frame_pkt_bytes[3]
    comm_frame['txp']                           = frame_pkt_bytes[4]
    comm_frame['rxp']                           = frame_pkt_bytes[5]
    comm_frame['payload']['header']['nwk']      = frame_pkt_bytes[6]
    comm_frame['payload']['header']['nod']      = frame_pkt_bytes[7]
    comm_frame['payload']['header']['subnod']   = frame_pkt_bytes[8]
    comm_frame['payload']['header']['module']   = frame_pkt_bytes[9]
    comm_frame['payload']['header']['mode']     = frame_pkt_bytes[10]
    comm_frame['payload']['header']['sck']      = frame_pkt_bytes[11]
    comm_frame['payload']['header']['cmd']      = frame_pkt_bytes[12]
    comm_frame['payload']['data']               = frame_pkt_bytes[13:212]
    comm_frame['crc']                           =(frame_pkt_bytes[213]<<8)|frame_pkt_bytes[214]
    comm_frame['eot']                           = frame_pkt_bytes[215]

    # print("RX CRC:",hex(comm_frame['crc']) )
    
    return comm_frame


def is_hex(data):
    try:
        int(data, 16)
        return True
    except ValueError:
        return False
    
def convert_to_bytes(data):
    
    if is_hex(data):
        return binascii.unhexlify(data)
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode('utf-8')
    if isinstance(data, list):
        return bytes(data)
    raise TypeError("Unsupported data type for conversion to bytes")

# def convert_to_bytes(data):
#     if isinstance(data, str):
#         if len(data) % 2 != 0:
#             raise ValueError("Hex string length must be even")
#         return bytes.fromhex(data)
#     elif isinstance(data, bytes):
#         return data
#     elif isinstance(data, list):
#         return bytes(data)
#     raise TypeError("Unsupported data type for conversion to bytes")

def frame_the_tx_comm_pkt(des,orig,pkttyp,txp,rxp,nwk,node,subnode,module,mode,sock,cmd,data,data_le):
    
    if  data_le > 0 and data is not None:
        # Initialize the frame buffer
        pu8_frame_buff = [0] * (216)
        

        pu8_frame_buff[0] = FRAME_SOT
        
        pu8_frame_buff[1] = des
        
        pu8_frame_buff[2] = orig
        
        pu8_frame_buff[3] = pkttyp
        
        pu8_frame_buff[4] = txp
        pu8_frame_buff[5] = rxp

        pu8_frame_buff[6] = nwk
        pu8_frame_buff[7] = node
        pu8_frame_buff[8] = subnode
        pu8_frame_buff[9] = module
        pu8_frame_buff[10] = mode
        pu8_frame_buff[11] = sock
        pu8_frame_buff[12] = cmd

            
        # Append actual data
        if isinstance(data, str):
            data = data.encode('utf-8')  # Convert string to bytes
        
        if isinstance(data, bytes):
            data = list(data)  # Convert bytes to list of integers
        
        count = 0
        for x in range(13,data_le+12+1):
            pu8_frame_buff[x] = data[count]
            count += 1
        
       
        # Calculate the CRC from SOF to the end of data
        u32_calculatedcrc = tools_fletcher_checksum(pu8_frame_buff[:-3])

        
        #print("u32_calculatedcrc:",hex(u32_calculatedcrc),"LEN",len(pu8_frame_buff))
        # Append CRC of frame
        pu8_frame_buff[213] = (u32_calculatedcrc >> 8) & 0xFF
        pu8_frame_buff[214] = u32_calculatedcrc & 0xFF
        
        # Append end of frame
        pu8_frame_buff[215] = FRAME_EOT
        
        hex_string = ''.join(f"{byte:02X}" for byte in pu8_frame_buff)

        print(f"[Transmit] {format_hex_string(hex_string) }")

        return hex_string

    else:
        # MISRA-C Compliance
        return None
        
# data = [0x00,0x00,0x00,0x03,0x31]
# frame_the_rx_comm_pkt(0,1,2,0x7c,0x00,0,0,0,0,0,0,0,data,1)

def tx_comm_usb( msg):
    global usb_port
    usb_port.write(msg)

def display_rx_frame_field(frame):

    print(  "type:",type(frame['sot']                        ), "frame['sot']                        ",frame['sot']                         )                     
    print(  "type:",type(frame['dest']                       ), "frame['dest']                       ",frame['dest']                        )
    print(  "type:",type(frame['origin']                     ), "frame['origin']                     ",frame['origin']                      )
    print(  "type:",type(frame['pkt_typ']                    ), "frame['pkt_typ']                    ",frame['pkt_typ']                     )
    print(  "type:",type(frame['txp']                        ), "frame['txp']                        ",frame['txp']                         )
    print(  "type:",type(frame['rxp']                        ), "frame['rxp']                        ",frame['rxp']                         )
    print(  "type:",type(frame['payload']['header']['nwk']   ), "frame['payload']['header']['nwk']   ",frame['payload']['header']['nwk']    )
    print(  "type:",type(frame['payload']['header']['nod']   ), "frame['payload']['header']['nod']   ",frame['payload']['header']['nod']    )
    print(  "type:",type(frame['payload']['header']['subnod']), "frame['payload']['header']['subnod']",frame['payload']['header']['subnod'] )
    print(  "type:",type(frame['payload']['header']['module']), "frame['payload']['header']['module']",frame['payload']['header']['module'] )
    print(  "type:",type(frame['payload']['header']['mode']  ), "frame['payload']['header']['mode']  ",frame['payload']['header']['mode']   )
    print(  "type:",type(frame['payload']['header']['sck']   ), "frame['payload']['header']['sck']   ",frame['payload']['header']['sck']    )
    print(  "type:",type(frame['payload']['header']['cmd']   ), "frame['payload']['header']['cmd']   ",frame['payload']['header']['cmd']    )
    print(  "type:",type(frame['payload']['data']            ), "frame['payload']['data']            ",frame['payload']['data']             )
    print(  "type:",type(frame['crc']                        ), "frame['crc']                        ",frame['crc']                         )
    print(  "type:",type(frame['eot']                        ), "frame['eot']                        ",frame['eot']                         )


total_valid_evt_log_cnt = 0




def get_search_method_name(value):
    if 0 <= value < len(STATUS_EVENT_SEARCH_METHOD_NAMES):
        return STATUS_EVENT_SEARCH_METHOD_NAMES[value]
    return "UNKNOWN_METHOD"


def get_event_subclass_description(event_class, subclass):
    try:
        return STATUS_EVENT_SUB_CLASS_DESCRIPTIONS[event_class][subclass]
    except IndexError:
        return "UNKNOWN_CLASS_OR_SUBCLASS"

def get_event_class_value(evt_class):
    try:
        return STATUS_EVENT_CLASS_NAMES[evt_class]
    except IndexError:
        return "UNKNOWN_CLASS"
    
def get_event_status_value(evt_status):
    try:
        return STATUS_EVENT_STATUS_VALUE[evt_status]
    except IndexError:
        return "UNKNOWN_STATUS"

def get_event_type(evt_type):
    try:
        return STATUS_EVENT_TYPE_DESCRIPTIONS[evt_type]
    except IndexError:
        return "UNKNOWN_TYPE"



def get_event_description(event_type: int, event_subtype: int) -> str:
    try:
        return EVENT_DESCRIPTIONS[event_type][event_subtype]
    except IndexError:
        return "UNKNOWN_EVENT"



def strip_outer_brackets(msg):
    correct_msg =msg.strip()
    if msg.startswith("[") and msg.endswith("]"):
        correct_msg=msg.replace("['", "")
        correct_msg=correct_msg.replace("']","")
        
    return correct_msg 
    
def check_evt_descriptor_to_display(evttype ,evtsub_typ, rxpar0 , rxpar1 , rxpar2):
        value = 0
        # Take descriptor text if the type ,sub type within this range
        if ( ( EVTTYPE_ZONE == evttype ) and (  (6 == evtsub_typ ) or ( 7 == evtsub_typ )  )): #Supervisory fault look here
            pass
        elif ( ( EVTTYPE_SUPERVISED_INPUT == evttype )): #and (  (0 != evtsub_typ ) and ( 1 != evtsub_typ )  )): #Supervisory fault look here
            pass
        elif ( ( EVTTYPE_SUPERVISED_OUTPUT == evttype ) ):#and (  (0 != evtsub_typ ) and ( 1 != evtsub_typ )  )): #Supervisory fault look here    
            pass
        elif ( ( EVTTYPE_ZONE_INPUT == evttype ) ):#and (  (0 != evtsub_typ ) and ( 1 != evtsub_typ )  )): #Supervisory fault look here
            pass
        elif ( ( EVTTYPE_GENERAL_EQUIPMENT == evttype ) and (  4 == evtsub_typ ) ): #Supervisory fault look here
            pass
        elif ( ( EVTTYPE_ZONE_EQUIPMENT == evttype ) and (  4 == evtsub_typ ) ): #Supervisory fault look here
            pass
        elif ( ( EVTTYPE_AREA_EQUIPMENT == evttype ) and (  4 == evtsub_typ ) ): #Supervisory fault look here
            pass
        elif ( ( EVTTYPE_EXT_ZONE_EQUIPMENT == evttype ) and (  4 == evtsub_typ ) ): #Supervisory fault look here
            pass
        
        else:
            value = 1


        return value


def get_event_identifier(evttype , rxpar0 , rxpar1 , rxpar2)-> str:
    return_identifier = "-"

    # Still not concluded based on how to read the identifier so we are reading only for some types only the identifier
    try :
        #Param0 value taking from the dictionary 
        #TESTED THIS IF -> PASS 
        if (    (  EVTTYPE_ZONE == evttype  ) or
                (  EVTTYPE_SUPERVISED_INPUT == evttype  ) or
                (  EVTTYPE_SUPERVISED_OUTPUT == evttype  ) or
                (  EVTTYPE_ZONE_INPUT == evttype  ) or
                (  EVTTYPE_EXT_ZONE == evttype  ) 
            ):
            value_par0=event_param0_number_name_list[evttype].format(par0=rxpar0)
            
            value_par1=supervisoryfault_param1_2_name[rxpar1]
            
            return_identifier = (value_par0+" "+value_par1)
            
        #Param1 value taking from list and disctionary
        #TESTED THIS ELIF -> PASS
        elif ( (  EVTTYPE_ZONE_EQUIPMENT == evttype  ) or
            (  EVTTYPE_AREA_EQUIPMENT == evttype  ) or
            (  EVTTYPE_EXT_ZONE_EQUIPMENT == evttype  ) 
            ):
            value_par0=STATUS_EVENT_DESCRIPTION_VALUE[evttype][rxpar0][0][0]
            
            value_par1=event_param1_number_name_list[evttype].format(par1=rxpar1)
            
            value_par2=supervisoryfault_param1_2_name[rxpar2]
            
            return_identifier = (value_par0+" "+value_par1+" "+value_par2)
        else:
            return_identifier =STATUS_EVENT_DESCRIPTION_VALUE[evttype][rxpar0][rxpar1][rxpar2]
            return_identifier = strip_outer_brackets(str(return_identifier))
    except:
        return return_identifier

    return return_identifier

def display_evtlog_like_solar_tool(evt_data):
    global total_valid_evt_log_cnt
    global evt_text_ascii
    # Convert to human-readable datetime
    timestamp = evt_data[17:21]
    timestamp_decimal=timestamp[3]|(timestamp[2]<<8)|(timestamp[1]<<16)|(timestamp[0]<<24)

    
    if 0x00 != timestamp_decimal :
        total_valid_evt_log_cnt+=1

        eventtime=tsconverter.CLOCK_TimeFromTimeStamp( timestamp_decimal)

        evt_text=evt_data[47:]
        #check the present text length
        if 0x00 != evt_text[1] :
            evt_text_value = evt_text[ 2: evt_text[1]+2]
            evt_text_ascii = "".join(chr(i) for i in evt_text_value)
        else:
            evt_text_ascii = "NO-TEXT"

        event_id =evt_data[4]|evt_data[3]<<8|evt_data[2]<<16|evt_data[1]<<24

        event_identifier_msg = ""
        event_descriptor_msg = ""

        if 1 == check_evt_descriptor_to_display(evt_data[14],evt_data[16], evt_data[34], evt_data[35], evt_data[36]) :
            event_identifier_msg = "-"
            event_descriptor_msg = get_event_description(evt_data[14], evt_data[16])
        else:
            event_descriptor_msg = get_event_description(evt_data[14], evt_data[16])
            event_identifier_msg = get_event_identifier(evt_data[14], evt_data[34], evt_data[35], evt_data[36])
                                        
        # print(
        #         f"{'EVENT-ID':<9}{'STATUS SEARCH METHOD':<26}{'EVTLOG DATE':<16}"
        #         f"{'EVTLOG TIME':<16}{'EVENT STATUS':<18}{'EVENT CLASS':<20}"
        #         f"{'EVENT TYPE':<21}{'EVENT':<22}{'IDENTIFIER':<25}TEXT"
        #     )
        # print(
        #         f"{event_id+1:<9}{get_search_method_name(evt_data[0]):<26}{dt.strftime('%d-%m-%Y'):<16}"
        #         f"{dt.strftime('%H:%M:%S'):<16}{get_event_status_value(evt_data[15]):<18}"
        #         f"{get_event_class_value(evt_data[12]):<20}{get_event_type(evt_data[14]):<21}"
        #         f"{event_descriptor_msg:<22}"
        #         f"{event_identifier_msg:<25}"
        #         f"{evt_text_ascii}"
        #     )

#    print(F" STATUS NODE NUMBER             :{evt_data[5]} ")
#         print(F" STATUS SUB NODE NUMBER         :{evt_data[6]} ")
#         print(F" STATUS MODULE NUMBER           :{evt_data[7]} ")
        #if node , subnode and module is (0,0,0) then the source is application,solar
        #if node=1 , subnode=1 and module=0 is (1,1,0) then the source is panel
        if (0==evt_data[5]) and  (0==evt_data[6]) and  (0==evt_data[7]):
            print("Source : SOLAR")
        elif (1==evt_data[5]) and  (1==evt_data[6]) and  (0==evt_data[7]):    
            print(f"Source:Panel No.{evt_data[5]}")
        else:
            pass
            

        print(
                f"{'EVENT-ID':<12}{'PANEL NO.':<12}{'L-BUS NO.':<12}{'MODULE NO.':<12}{'EVTLOG DATE':<16}"
                f"{'EVTLOG TIME':<16}{'EVENT STATUS':<18}{'EVENT CLASS':<20}"
                f"{'EVENT TYPE':<21}{'EVENT':<28}{'IDENTIFIER':<28}TEXT"
            )
        print(
                f"{event_id+1:<12}{evt_data[5]:<12}{evt_data[6]:<12}{evt_data[7]:<12}{eventtime.Day:02}/{eventtime.Month:02}/{eventtime.Year:<10}"
                f"{eventtime.Hour:02}:{eventtime.Minute:02}:{eventtime.Second:<12}{get_event_status_value(evt_data[15]):<18}"
                f"{get_event_class_value(evt_data[12]):<20}{get_event_type(evt_data[14]):<21}"
                f"{event_descriptor_msg:<28}"
                f"{event_identifier_msg:<28}"
                f"{evt_text_ascii}"
            )
    else:
        pass


def display_evtlog_payload_field(evt_data):
    global total_valid_evt_log_cnt
    # Convert to human-readable datetime
    timestamp = evt_data[17:21]
    timestamp_decimal=timestamp[3]|(timestamp[2]<<8)|(timestamp[1]<<16)|(timestamp[0]<<24)

    
    if 0x00 != timestamp_decimal :
        total_valid_evt_log_cnt+=1
        # dt = datetime.datetime.utcfromtimestamp(timestamp_decimal)

        print(F" STATUS SEARCH METHOD           :{evt_data[0]} ")
        print(F" STATUS SEARCH NUMBER           :{evt_data[1:5]} ")#4bytes
        print(F" STATUS NODE NUMBER             :{evt_data[5]} ")
        print(F" STATUS SUB NODE NUMBER         :{evt_data[6]} ")
        print(F" STATUS MODULE NUMBER           :{evt_data[7]} ")
        print(F" STATUS EVENT COUNT             :{evt_data[8:12]} ")#4BYTES
        print(F" STATUS EVENT CLASS             :{evt_data[12]} ")
        print(F" STATUS SUB CLASS               :{evt_data[13]} ")
        print(F" STATUS EVENT TYPE              :{evt_data[14]} ")
        print(F" STATUS EVENT STATUS            :{evt_data[15]} ")
        print(F" STATUS EVENT SUB-TYPE          :{evt_data[16]} ")
        print(F" STATUS EVENT TIMESTAMP         :{bytes(evt_data[17:21]).hex()} ")#4BYTES
        print(F" STATUS EVENT I/O NUMBER TYPE   :{evt_data[21]} ")
        print(F" STATUS EVENT I/O NUMBER        :{evt_data[22:24]} ")#2bytes
        print(F" STATUS EVENT I/O DATA-0        :{evt_data[24]} ")
        print(F" STATUS EVENT I/O DATA-1        :{evt_data[25]} ")
        print(F" STATUS EVENT I/O DATA-2        :{evt_data[26]} ")
        print(F" STATUS EVENT I/O DATA-3        :{evt_data[27]} ")
        print(F" STATUS EVENT I/O DATA-4        :{evt_data[28]} ")
        print(F" STATUS EVENT I/O DATA-5        :{evt_data[29]} ")
        print(F" STATUS EVENT I/O DATA-6        :{evt_data[30]} ")
        print(F" STATUS EVENT I/O DATA-7        :{evt_data[31]} ")
        print(F" STATUS EVENT I/O DATA-8        :{evt_data[32]} ")
        print(F" STATUS EVENT I/O DATA-9        :{evt_data[33]} ")
        print(F" STATUS EVENT I/O PARAM-0       :{evt_data[34]} ")
        print(F" STATUS EVENT I/O PARAM-1       :{evt_data[35]} ")
        print(F" STATUS EVENT I/O PARAM-2       :{evt_data[36]} ")
        print(F" STATUS ACTIVE EVENT COUNT      :{evt_data[37:41]} ")#4BYTES
        print(F" STATUS ACTIVE EVENT CLASS COUNT:{evt_data[41:45]} ")#4BYTES
        print(F" STATUS TS OUTPUT TYPE          :{evt_data[45]} ")
        print(F" STATUS TS OUTPUT NUMBER        :{evt_data[46]} ")
        print(F" STATUS EVENT TEXT              :{evt_data[47:]} ")
    else:
        pass

    # print(F"  STATUC EVENT TEXT-1            :{evt_data[0]} ")
    # print(F"  STATUC EVENT TEXT-2            :{evt_data[0]} ")

def process_evt_log(evtlog):
    # print(" <<<<<<<<<<<<<<<<<<<<<<<<<<<<< RX EVENT-LOG >>>>>>>>>>>>>>>>>>>>>>>>>>")
    # print(F"EVENT LOG DATA:{evtlog['payload']['data']}")
    display_evtlog_payload_field(evtlog['payload']['data'])
    display_evtlog_like_solar_tool(evtlog['payload']['data'])


def rx_frame_process(rx_frame,rx_frame_len):
    global process_state
    global main_process_statemachine
    global PKTRX_CNT
    global LOG_EVT_SERACH_NUMBER
    global running
    
    parsed_Frame = parse_and_update_rx_comm_pkt(rx_frame,rx_frame_len)
    # display_rx_frame_field(parsed_Frame)#Display the frame data

    # print("process_state:",process_state)
    if REQ_NWK_PKT == process_state:
        if NWK_PKT == parsed_Frame['pkt_typ']:
            print("<<<<<<<<<<<< RX NETWORK PACKET >>>>>>>>>>>>>>>>>>>\n")
            process_state == REQ_ACCESS_KEY
            main_process_statemachine = REQ_ACCESS_KEY
        else:
            print("<<<<<<<<<<<< RX NACK FOR NETWORK PACKET >>>>>>>>>>>>>>>>>>>\n")
            process_state == REQ_NWK_PKT
            main_process_statemachine = REQ_NWK_PKT

    elif REQ_ACCESS_KEY == process_state :
        if ACK_PKT == parsed_Frame['pkt_typ'] :
            print("<<<<<<<<<<<< RX ACCESS KEY ACK PACKET >>>>>>>>>>>>>>>>>>>\n")
            process_state = DUMMYPKT_SEND
            main_process_statemachine = DUMMYPKT_SEND
        else:
            print("<<<<<<<<<<<< RX ACCESS KEY NACK PACKET >>>>>>>>>>>>>>>>>>>\n")
            process_state = REQ_NWK_PKT
            main_process_statemachine = REQ_NWK_PKT
        
    elif process_state == DUMMYPKT_SEND:
            if NRM_PKT == parsed_Frame['pkt_typ'] and ( DB_STATUS_INSTRUCT_MODE == parsed_Frame['payload']['header']['mode']) :
                ascii_list = parsed_Frame['payload']['data'][1:5]
                ascii_str = ''.join([chr(x) for x in ascii_list])

                print("ascii_str :",ascii_str )
                if( ascii_str   == '1974' ):
                    print("<<<<<<<<<<<< RX ACCESS KEY PACKET >>>>>>>>>>>>>>>>>>>\n")
                    process_state = READ_EVT_LOG
                    main_process_statemachine = READ_EVT_LOG
                else:
                    print("<<<<<<<<<<<< RX INVALID PACKET FOR ACCESS KEY >>>>>>>>>>>>>>>>>>>\n")
                    process_state = REQ_NWK_PKT
                    main_process_statemachine = REQ_NWK_PKT
            else:
                print("<<<<<<<<<<<< RX ACCESS KEY NACK PACKET >>>>>>>>>>>>>>>>>>>\n")
                process_state = REQ_NWK_PKT
                main_process_statemachine = REQ_NWK_PKT

    elif process_state == READ_EVT_LOG:
        if NRM_PKT == parsed_Frame['pkt_typ']:
            if (DB_SETUP_REQ_MODE == parsed_Frame['payload']['header']['mode']) and \
                (EVENT_STATUS_CMD == parsed_Frame['payload']['header']['cmd'] ):
                print(f"<<<<<<<<<<<< RX EVENT LOG-TX PKT NUM:{hex(parsed_Frame['txp'])} RX PKT NUM:{hex(parsed_Frame['rxp'])} >>>>>>>>>>>>>>>>>>>\n")
                process_state = READ_EVT_LOG
                main_process_statemachine = READ_EVT_LOG
                process_evt_log(parsed_Frame)
                # running = 0
            else:
                print("<<<<<<<<<<<< INVALID EVENT STATUS LOG PACKET >>>>>>>>>>>>>>>>>>>\n")
                process_state = REQ_NWK_PKT
                main_process_statemachine = REQ_NWK_PKT
        else:
            print(f"<<<<<<<<<<<< INVALID EVENT STATUS LOG PACKET {parsed_Frame['pkt_typ']} >>>>>>>>>>>>>>>>>>>\n")

    PKTRX_CNT = parsed_Frame['txp']
    if 1 == stop_evt_log_read:
        print(f" ================= Read 1000 logs [total_evt_log_cnt:{total_valid_evt_log_cnt}]=========================")
        running = 0

def read_from_port(port):
    global rx_poll_rsp
    # global usb_port
    while running:
        try:
            if port.in_waiting > 0:
                data = port.read(216)
                print(f"\n[Received] {data.hex(' ')}")
                rx_poll_rsp = 1
                rx_frame_process(data,len(data))

        except serial.SerialException:
            print("Serial port closed or error.")
            break

def req_nwk_pkt():
    global process_state
    global PKTTX_CNT
    global PKTRX_CNT
    global LOG_EVT_SERACH_NUMBER
    global main_process_statemachine
    global total_valid_evt_log_cnt
    global stop_evt_log_read
    total_valid_evt_log_cnt = 0
    PKTTX_CNT = 0
    PKTRX_CNT = 0
    LOG_EVT_SERACH_NUMBER = 0x000003E8   # 1000 th log number
    print("<<<<<<<<<<<<<<<<<<<<<<<< Requesting network pakcet >>>>>>>>>>>>>>>>>>>>>>>>>>>")
    nwk_req_pkt=bytes( [0xfe, 0x01, 0x00, 0x04, PKTTX_CNT, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0xb1, 0x4a, 0xfd])
    
    tx_comm_usb(nwk_req_pkt)
    process_state = REQ_NWK_PKT
    
    main_process_statemachine = REQ_RSP_WAIT_STATE
    print("process_state",process_state)
    PKTTX_CNT+=1
    stop_evt_log_read = 0

def req_access_key():
    global PKTTX_CNT
    global process_state
    global main_process_statemachine

    print("<<<<<<<<<<<<<<<<<<<<<<<< Requesting access key    >>>>>>>>>>>>>>>>>>>>>>>>>>>")
    accesskey_req_pkt=bytes( [0xfe, 0x01, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x83, 0x00, 0x04, 0x04, 0x31, 0x39, 0x37, 0x34, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x70, 0x2c, 0xfd])

    tx_comm_usb(accesskey_req_pkt)

    process_state = REQ_ACCESS_KEY

    main_process_statemachine = REQ_RSP_WAIT_STATE
    print("process_state",process_state)
    PKTTX_CNT+=1

def req_evt_log():
    global LOG_EVT_SERACH_NUMBER
    global PKTTX_CNT
    global process_state
    global main_process_statemachine
    global running
    global stop_evt_log_read
    # print("<<<<<<<<<<<<<<<<<<<<<<<< Requesting event log >>>>>>>>>>>>>>>>>>>>>>>>>>>")
    

    if 255 == PKTTX_CNT:
        PKTTX_CNT =0

    evt_log_payload_data=[LOG_EVT_SEARCH_METHOD,(LOG_EVT_SERACH_NUMBER>>24)&0xff,(LOG_EVT_SERACH_NUMBER>>16)&0xff,(LOG_EVT_SERACH_NUMBER>>8)&0xff,LOG_EVT_SERACH_NUMBER&0xff]

    frame_packet = frame_the_tx_comm_pkt(SCRIPT_DEST , SCRIPT_ORIG , NRM_PKT,PKTTX_CNT,PKTRX_CNT,LOG_NW , LOG_ND ,LOG_SND , LOG_MO , LOG_MD , LOG_SK , LOG_CMD ,evt_log_payload_data,5 )
    tx_pkt=convert_to_bytes(frame_packet)
    # print("Len:",len(tx_pkt),"TYPE:",type(tx_pkt),"tx_pkt:",tx_pkt)
    tx_comm_usb(tx_pkt)
    
    if 0x00 == LOG_EVT_SERACH_NUMBER:
        stop_evt_log_read = 1
    else:    
        LOG_EVT_SERACH_NUMBER-=1

    # tx_pkt=bytes( [0xfe, 0x01, 0x00, 0x01, 0x03, 0x02, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x02, 0x04, 0x00, 0x00, 0x03, 0xe7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0x16, 0xfd])
    # print("Len:",len(tx_pkt),"TYPE:",type(tx_pkt),"tx_pkt:",tx_pkt)
    # tx_comm_usb(tx_pkt)


    PKTTX_CNT+=1
    process_state = READ_EVT_LOG
    main_process_statemachine = REQ_RSP_WAIT_STATE
    
    # print("process_state:",process_state)

def send_dummy_pkt():
    global LOG_EVT_SERACH_NUMBER
    global PKTTX_CNT
    global process_state
    global main_process_statemachine

    print("<<<<<<<<<<<<<<<<<<<<<<<< Requesting dummy packet for access key >>>>>>>>>>>>>>>>>>>>>>>>>>>")
    LOG_EVT_SERACH_NUMBER-=1
    evt_log_payload_data=[LOG_EVT_SEARCH_METHOD,(LOG_EVT_SERACH_NUMBER>>24)&0xff,(LOG_EVT_SERACH_NUMBER>>16)&0xff,(LOG_EVT_SERACH_NUMBER>>8)&0xff,LOG_EVT_SERACH_NUMBER&0xff]

    frame_packet = frame_the_tx_comm_pkt(SCRIPT_DEST , SCRIPT_ORIG , NRM_PKT,PKTTX_CNT,PKTRX_CNT,LOG_NW , LOG_ND ,LOG_SND , LOG_MO , LOG_MD , LOG_SK , LOG_CMD ,evt_log_payload_data,5 )
    tx_pkt=convert_to_bytes(frame_packet)
    # print("Len:",len(tx_pkt),"TYPE:",type(tx_pkt),"tx_pkt:",tx_pkt)
    
    tx_comm_usb(tx_pkt)


    # tx_pkt=bytes([0xfe, 0x01, 0x00, 0x01, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x02, 0x04, 0x00, 0x00, 0x03, 0xe7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x95, 0x73, 0xfd])
    # print("Len:",len(tx_pkt),"TYPE:",type(tx_pkt),"tx_pkt:",tx_pkt)
    # tx_comm_usb(tx_pkt)

    PKTTX_CNT+=1
    process_state = DUMMYPKT_SEND
    main_process_statemachine = REQ_RSP_WAIT_STATE
    
    print("process_state:",process_state)


def panel_process():
    
    if REQ_NWK_PKT      == main_process_statemachine :
        
        time.sleep(5)
        req_nwk_pkt()
        
    elif REQ_ACCESS_KEY == main_process_statemachine:
        time.sleep(2)
        req_access_key()
    elif DUMMYPKT_SEND == main_process_statemachine:
        time.sleep(2)
        send_dummy_pkt()

    elif READ_EVT_LOG   == main_process_statemachine :
        req_evt_log()

    elif REQ_RSP_WAIT_STATE == main_process_statemachine:
        # print("<<<<<<<<<<<<<<<<<<<<<<<< Waiting for the response >>>>>>>>>>>>>>>>>>>>>>>>>>>")
        time.sleep(0.1)

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def connect_to_the_usb_comm():
    global panel_connecte_state
    port_name = "COM3"
    baudrate = 115200
    global usb_port

    try:
        usb_port = serial.Serial(port_name, baudrate, timeout=0.1)
        print(f"Connected to {port_name} at {baudrate} baud.")
        panel_connecte_state = PANEL_CONNECTED
    except Exception as e:
        print(f"Failed to connect: {e}")
        return
    
usb_port = None
def main():
    
    global usb_port
    global panel_connecte_state

    signal.signal(signal.SIGINT, signal_handler)  # Catch Ctrl+C




    # threading.Thread(target=poll_task).start()
    # global usb_port
    # Idle loop to keep main thread alive
    while running:
        if PANEL_NOT_CONNECTED == panel_connecte_state:
            connect_to_the_usb_comm()
            if usb_port != None:
                threading.Thread(target=read_from_port,args=(usb_port,)).start()
            else:
                print("USB port not connected.")
                time.sleep(1)
                continue

        elif PANEL_CONNECTED == panel_connecte_state:
            panel_connecte_state = PANEL_PROCESS

        elif PANEL_PROCESS == panel_connecte_state:
            panel_process()

if __name__ == "__main__":
    main()
