import 'dart:async';
import 'dart:typed_data';
import 'package:techno_switch_rhino_103_controller/models/comm_frame.dart';
import 'package:usb_serial/usb_serial.dart';
import 'package:usb_serial/transaction.dart';
import '../constants/event_types.dart';
import '../models/event_log.dart';

class UsbSerialService {
  UsbPort? _port;
  StreamSubscription<Uint8List>? _subscription;
  Transaction<Uint8List>? _transaction;
  UsbDevice? _device;
  
  int _processState = EventTypes.REQ_NWK_PKT;
  int _mainProcessState = EventTypes.REQ_NWK_PKT;
  int _panelConnectedState = EventTypes.PANEL_NOT_CONNECTED;
  int _pkttxCnt = 0;
  int _pktrxCnt = 0;
  int _logEvtSearchNumber = EventTypes.LOG_EVT_SEARCH_NUMBER;
  bool _stopEvtLogRead = false;
  int _totalValidEvtLogCnt = 0;

  final StreamController<String> _logController = StreamController<String>.broadcast();
  Stream<String> get logStream => _logController.stream;

  List<int> _buffer = [];

  static const int MAX_RETRIES = 3;
  static const int RESPONSE_TIMEOUT = 2000; // 2 seconds timeout
  int _retryCount = 0;
  Timer? _responseTimer;
  Timer? _processTimer;

  bool _accessKeyRequestScheduled = false;
  bool _dummyPacketScheduled = false;

  void _log(String message) {
    print('[EventLogger] $message');
    _logController.add(message);
  }

  Future<List<UsbDevice>> getDevices() async {
    return await UsbSerial.listDevices();
  }

  Future<bool> connect(UsbDevice device) async {
    try {
      await disconnect();

      _port = await device.create();
      if (!await _port!.open()) {
        _log('Failed to open port');
        return false;
      }

      // Configure port
      try {
        await _port!.setPortParameters(
          115200,
          UsbPort.DATABITS_8,
          UsbPort.STOPBITS_1,
          UsbPort.PARITY_NONE,
        );
        await Future.delayed(const Duration(milliseconds: 100));

        await _port!.setDTR(true);
        await _port!.setRTS(true);
        await Future.delayed(const Duration(milliseconds: 100));
      } catch (e) {
        _log('Port configuration failed: $e');
        return false;
      }

      _device = device;
      _buffer.clear();
      
      _subscription = _port!.inputStream!.listen(
        (data) {
          _log('Received data: ${data.length} bytes');
          _log('Raw data: ${data.map((e) => e.toRadixString(16).padLeft(2, '0')).join(' ')}');
          _onDataReceived(data);
        },
        onError: (error) {
          _log('Error on input stream: $error');
          _resetStates();
        },
        onDone: () {
          _log('Input stream closed');
          _resetStates();
        },
        cancelOnError: false,
      );

      _panelConnectedState = EventTypes.PANEL_CONNECTED;
      _log('Connected to device');

      // Reset all states to initial values
      _resetStates();

      // Start the process timer to match Python's behavior
      _startProcessTimer();

      // Transition to PANEL_PROCESS state after a short delay
      Future.delayed(const Duration(milliseconds: 500), () {
        _log('Transitioning to PANEL_PROCESS state');
        _panelConnectedState = EventTypes.PANEL_PROCESS;
        // Ensure we start with network packet request
        _processState = EventTypes.REQ_NWK_PKT;
        _mainProcessState = EventTypes.REQ_NWK_PKT;
      });

      return true;
    } catch (e) {
      _log('Error connecting to device: $e');
      return false;
    }
  }

  void _resetStates() {
    _processState = EventTypes.REQ_NWK_PKT;
    _mainProcessState = EventTypes.REQ_NWK_PKT;
    _pkttxCnt = 0;
    _pktrxCnt = 0;
    _logEvtSearchNumber = EventTypes.LOG_EVT_SEARCH_NUMBER;
    _stopEvtLogRead = false;
    _totalValidEvtLogCnt = 0;
    _retryCount = 0;
    _responseTimer?.cancel();
    _responseTimer = null;
  }

  void _startProcessTimer() {
    _processTimer?.cancel();
    _processTimer = Timer.periodic(const Duration(milliseconds: 100), (timer) {
      if (_panelConnectedState == EventTypes.PANEL_PROCESS) {
        _log('Process timer tick - Panel state: $_panelConnectedState, Process state: $_processState, Main state: $_mainProcessState');
        _panelProcess();
      }
    });
  }

  void _panelProcess() {
    // Don't process if we're waiting for a response
    if (_mainProcessState == EventTypes.REQ_RSP_WAIT_STATE) {
        Future.delayed(const Duration(milliseconds: 100), () {
            // Just wait, like Python's time.sleep(0.1)
        });
        return;
    }

    switch (_mainProcessState) {
        case EventTypes.REQ_NWK_PKT:
            _log('In REQ_NWK_PKT state');
            Future.delayed(const Duration(milliseconds: 1670), () {  // Updated to match flow
                if (_panelConnectedState == EventTypes.PANEL_PROCESS) {
                    _sendNetworkPacket();
                }
            });
            break;

        case EventTypes.REQ_ACCESS_KEY:
            _log('In REQ_ACCESS_KEY state');
            Future.delayed(const Duration(milliseconds: 1550), () {  // Updated to match flow
                if (_panelConnectedState == EventTypes.PANEL_PROCESS) {
                    _sendAccessKeyPacket();
                }
            });
            break;

        case EventTypes.DUMMYPKT_SEND:
            _log('In DUMMYPKT_SEND state');
            Future.delayed(const Duration(milliseconds: 2810), () {  // Updated to match flow
                if (_panelConnectedState == EventTypes.PANEL_PROCESS) {
                    _sendDummyPacket();
                }
            });
            break;

        case EventTypes.READ_EVT_LOG:
            _log('In READ_EVT_LOG state');
            Future.delayed(const Duration(milliseconds: 2360), () {  // Updated to match flow
                if (_panelConnectedState == EventTypes.PANEL_PROCESS) {
                    _requestEventLog();
                }
            });
            break;
    }
  }

  Future<void> requestNetworkPacket() async {
    _log('Network packet request queued - will be sent by state machine');
    // Reset states to ensure we start fresh
    _resetStates();
  }

  Future<void> _sendNetworkPacket() async {
    try {
        _log('<<<<<<<<<<<<<<<<<<<<<<<< Requesting network packet >>>>>>>>>>>>>>>>>>>>>>>>>>>');
        
        // Create network request packet exactly matching Python script
        List<int> nwkReqPkt = List<int>.filled(216, 0x00);
        nwkReqPkt[0] = EventTypes.FRAME_SOT;  // 0xFE
        nwkReqPkt[1] = 0x01;  // dest
        nwkReqPkt[2] = 0x00;  // origin
        nwkReqPkt[3] = EventTypes.NWK_PKT;  // 0x04
        nwkReqPkt[4] = _pkttxCnt;  // txp
        nwkReqPkt[5] = 0x00;  // rxp

        // Use hardcoded CRC values from Python script
        nwkReqPkt[213] = 0xB1;  // CRC high byte
        nwkReqPkt[214] = 0x4A;  // CRC low byte
        nwkReqPkt[215] = EventTypes.FRAME_EOT;

        _log('[TX] ${nwkReqPkt.map((e) => e.toRadixString(16).padLeft(2, '0').toUpperCase()).join(' ')}');
        await _port?.write(Uint8List.fromList(nwkReqPkt));

        _processState = EventTypes.REQ_NWK_PKT;
        _mainProcessState = EventTypes.REQ_RSP_WAIT_STATE;
        _pkttxCnt++;
        _stopEvtLogRead = false;

    } catch (e) {
        _log('[Error] Error sending network packet: $e');
        _resetStates();
    }
  }

  int _calculateCRC(List<int> data) {
    int sum1 = 0;
    int sum2 = 0;
    
    for (int i = 0; i < data.length; i++) {
      sum1 = (sum1 + data[i]) % 255;
      sum2 = (sum2 + sum1) % 255;
    }

    int chk1 = (255 - ((sum1 + sum2) % 255)) % 255;
    int chk2 = (255 - ((sum1 + chk1) % 255)) % 255;

    return (chk1 << 8) | chk2;
  }

  Future<void> requestAccessKey() async {
    _log('Requesting access key...');
    _retryCount = 0;
    await _sendAccessKeyPacket();
  }

  Future<void> _sendAccessKeyPacket() async {
    try {
        _log('<<<<<<<<<<<<<<<<<<<<<<<< Requesting access key >>>>>>>>>>>>>>>>>>>>>>>>>>>');
        
        // Create access key packet exactly matching Python script
        List<int> accessKeyPkt = List<int>.filled(216, 0x00);
        accessKeyPkt[0] = EventTypes.FRAME_SOT;  // 0xFE
        accessKeyPkt[1] = 0x01;  // dest
        accessKeyPkt[2] = 0x00;  // origin
        accessKeyPkt[3] = EventTypes.NRM_PKT;  // 0x01
        accessKeyPkt[4] = 0x01;  // txp - Hardcoded to match Python script
        accessKeyPkt[5] = 0x00;  // rxp
        
        // Header
        accessKeyPkt[6] = 0x00;  // nwk
        accessKeyPkt[7] = 0x00;  // nod
        accessKeyPkt[8] = 0x00;  // subnod
        accessKeyPkt[9] = 0x00;  // module
        accessKeyPkt[10] = 0x83;  // mode (DB_STATUS_INSTRUCT_MODE)
        accessKeyPkt[11] = 0x00;  // sck
        accessKeyPkt[12] = 0x04;  // cmd
        
        // Access key data
        accessKeyPkt[13] = 0x04;  // Access key method
        accessKeyPkt[14] = 0x31;  // ASCII '1'
        accessKeyPkt[15] = 0x39;  // ASCII '9'
        accessKeyPkt[16] = 0x37;  // ASCII '7'
        accessKeyPkt[17] = 0x34;  // ASCII '4'

        // Use hardcoded CRC values from Python script
        accessKeyPkt[213] = 0x70;  // CRC high byte
        accessKeyPkt[214] = 0x2C;  // CRC low byte
        accessKeyPkt[215] = EventTypes.FRAME_EOT;

        _log('[TX] ${accessKeyPkt.map((e) => e.toRadixString(16).padLeft(2, '0').toUpperCase()).join(' ')}');
        await _port?.write(Uint8List.fromList(accessKeyPkt));

        _processState = EventTypes.REQ_ACCESS_KEY;
        _mainProcessState = EventTypes.REQ_RSP_WAIT_STATE;
        _pkttxCnt++;

    } catch (e) {
        _log('[Error] Error sending access key packet: $e');
        _resetStates();
    }
  }

  Future<void> _requestEventLog() async {
    try {
        if (_pkttxCnt == 255) {
            _pkttxCnt = 0;
        }

        List<int> evtLogPayloadData = [
            EventTypes.LOG_EVT_SEARCH_METHOD,
            (_logEvtSearchNumber >> 24) & 0xff,
            (_logEvtSearchNumber >> 16) & 0xff,
            (_logEvtSearchNumber >> 8) & 0xff,
            _logEvtSearchNumber & 0xff
        ];

        CommFrame frame = CommFrame(
            sot: EventTypes.FRAME_SOT,
            dest: EventTypes.SCRIPT_DEST,
            origin: EventTypes.SCRIPT_ORIG,
            pktTyp: EventTypes.NRM_PKT,
            txp: _pkttxCnt,
            rxp: _pktrxCnt,
            payload: CommData(
                header: CommHeader(
                    nwk: EventTypes.LOG_NW,
                    nod: EventTypes.LOG_ND,
                    subnod: EventTypes.LOG_SND,
                    module: EventTypes.LOG_MO,
                    mode: EventTypes.LOG_MD,
                    sck: EventTypes.LOG_SK,
                    cmd: EventTypes.LOG_CMD,
                ),
                data: [...evtLogPayloadData, ...List<int>.filled(195, 0x00)],
            ),
            eot: EventTypes.FRAME_EOT,
        );

        await _port?.write(frame.toBytes());

        if (_logEvtSearchNumber == 0) {
            _stopEvtLogRead = true;
        } else {
            _logEvtSearchNumber--;
        }

        _processState = EventTypes.READ_EVT_LOG;
        _mainProcessState = EventTypes.REQ_RSP_WAIT_STATE;
        _pkttxCnt++;

    } catch (e) {
        _log('[Error] Error requesting event log: $e');
        _resetStates();
    }
  }

  void _onDataReceived(Uint8List data) {
    _log('[RX] ${data.map((e) => e.toRadixString(16).padLeft(2, '0').toUpperCase()).join(' ')}');
    
    // Add new data to buffer
    _buffer.addAll(data);
    
    // Process buffer while we can find complete frames
    while (_buffer.length >= EventTypes.COMM_EACH_FRAME_SIZE) {
        // Look for frame start
        int startIndex = _buffer.indexOf(EventTypes.FRAME_SOT);
        if (startIndex == -1) {
            _buffer.clear();
            return;
        }

        // Remove any data before the SOT
        if (startIndex > 0) {
            _buffer.removeRange(0, startIndex);
        }

        // Check if we have a complete frame
        if (_buffer.length < EventTypes.COMM_EACH_FRAME_SIZE) {
            return;
        }

        // Extract and process the frame
        List<int> frameData = _buffer.sublist(0, EventTypes.COMM_EACH_FRAME_SIZE);
        _buffer.removeRange(0, EventTypes.COMM_EACH_FRAME_SIZE);

        try {
            _processFrame(frameData);

        } catch (e) {
            _log('[Error] Error processing received frame: $e');
            _resetStates();
        }
    }
  }

  void _processFrame(List<int> frameData) {
    try {
      // Extract basic frame fields
      int pktType = frameData[3];
      int txp = frameData[4];
      int rxp = frameData[5];
      int mode = frameData[10];
      int cmd = frameData[12];

      _pktrxCnt = txp;

      // Match Python script's state transitions exactly
      if (_processState == EventTypes.REQ_NWK_PKT) {
        if (pktType == EventTypes.NWK_PKT) {
          _log('<<<<<<<<<<<< RX NETWORK PACKET >>>>>>>>>>>>>>>>>>>>>>>>>>>');
          _processState = EventTypes.REQ_ACCESS_KEY;
          _mainProcessState = EventTypes.REQ_ACCESS_KEY;
        } else {
          _log('<<<<<<<<<<<< RX NACK FOR NETWORK PACKET >>>>>>>>>>>>>>>>>>>>>>>>>>>');
          _processState = EventTypes.REQ_NWK_PKT;
          _mainProcessState = EventTypes.REQ_NWK_PKT;
        }
      } else if (_processState == EventTypes.REQ_ACCESS_KEY) {
        if (pktType == EventTypes.ACK_PKT) {
          _log('<<<<<<<<<<<< RX ACCESS KEY ACK PACKET >>>>>>>>>>>>>>>>>>>>>>>>>>>');
          _processState = EventTypes.DUMMYPKT_SEND;
          _mainProcessState = EventTypes.DUMMYPKT_SEND;
        } else {
          _log('<<<<<<<<<<<< RX ACCESS KEY NACK PACKET >>>>>>>>>>>>>>>>>>>>>>>>>>>');
          _processState = EventTypes.REQ_NWK_PKT;
          _mainProcessState = EventTypes.REQ_NWK_PKT;
        }
      } else if (_processState == EventTypes.DUMMYPKT_SEND) {
        if (pktType == EventTypes.NRM_PKT && mode == EventTypes.DB_STATUS_INSTRUCT_MODE) {
          List<int> asciiList = frameData.sublist(14, 18);
          String asciiStr = String.fromCharCodes(asciiList);
          
          if (asciiStr == '1974') {
            _log('<<<<<<<<<<<< RX ACCESS KEY PACKET >>>>>>>>>>>>>>>>>>>>>>>>>>>');
            _processState = EventTypes.READ_EVT_LOG;
            _mainProcessState = EventTypes.READ_EVT_LOG;
          } else {
            _log('<<<<<<<<<<<< RX INVALID PACKET FOR ACCESS KEY >>>>>>>>>>>>>>>>>>>>>>>>>>>');
            _processState = EventTypes.REQ_NWK_PKT;
            _mainProcessState = EventTypes.REQ_NWK_PKT;
          }
        } else {
          _log('<<<<<<<<<<<< RX ACCESS KEY NACK PACKET >>>>>>>>>>>>>>>>>>>>>>>>>>>');
          _processState = EventTypes.REQ_NWK_PKT;
          _mainProcessState = EventTypes.REQ_NWK_PKT;
        }
      } else if (_processState == EventTypes.READ_EVT_LOG) {
        if (pktType == EventTypes.NRM_PKT) {
          if (mode == EventTypes.DB_SETUP_REQ_MODE && cmd == EventTypes.EVENT_STATUS_CMD) {
            _log('<<<<<<<<<<<< RX EVENT LOG >>>>>>>>>>>>>>>>>>>>>>>>>>>');
            _processState = EventTypes.READ_EVT_LOG;
            _mainProcessState = EventTypes.READ_EVT_LOG;
            EventLog eventLog = EventLog.fromFrame(frameData);
            _log(eventLog.toString());
          } else {
            _log('<<<<<<<<<<<< INVALID EVENT STATUS LOG PACKET >>>>>>>>>>>>>>>>>>>>>>>>>>>');
            _processState = EventTypes.REQ_NWK_PKT;
            _mainProcessState = EventTypes.REQ_NWK_PKT;
          }
        } else {
          _log('<<<<<<<<<<<< INVALID EVENT STATUS LOG PACKET $pktType >>>>>>>>>>>>>>>>>>>>>>>>>>>');
        }
      }

      if (_stopEvtLogRead) {
        _resetStates();
      }

    } catch (e) {
      _log('[Error] Error processing received frame: $e');
      _resetStates();
    }
  }

  void _handleNetworkResponse(CommFrame frame) {
    if (frame.pktTyp == EventTypes.NWK_PKT) {
      _log('Received network response');
      _processState = EventTypes.REQ_ACCESS_KEY;
      _mainProcessState = EventTypes.REQ_ACCESS_KEY;
      _log('Valid network response, transitioning to REQ_ACCESS_KEY state');
      _scheduleAccessKeyRequest();
    } else {
      _log('Invalid network response type: ${frame.pktTyp}');
      _resetStates();
    }
  }

  void _handleAccessKeyResponse(CommFrame frame) {
    _log('Received access key response');
    _responseTimer?.cancel();
    _responseTimer = null;
    
    // Match Python script's state transition
    if (frame.pktTyp == EventTypes.ACK_PKT || frame.pktTyp == EventTypes.NRM_PKT) {
      _log('Valid access key response, transitioning to DUMMYPKT_SEND state');
      _processState = EventTypes.DUMMYPKT_SEND;
      _mainProcessState = EventTypes.DUMMYPKT_SEND;
      _retryCount = 0;  // Reset retry count
    } else {
      _log('Invalid access key response type: 0x${frame.pktTyp.toRadixString(16)}');
      _resetStates();
    }
    _log('Current process state: $_processState, main process state: $_mainProcessState');
  }

  void _handleEventLogResponse(CommFrame frame) {
    _log('Received event log response');
    // Process event log data
    if (frame.payload.header.mode == EventTypes.EVT_LOG_RSP) {
      _totalValidEvtLogCnt++;
      _log('Valid event log count: $_totalValidEvtLogCnt');
    }
  }

  Future<void> _sendDummyPacket() async {
    try {
        _log('<<<<<<<<<<<<<<<<<<<<<<<< Requesting dummy packet for access key >>>>>>>>>>>>>>>>>>>>>>>>>>>');
        
        // Create dummy packet exactly matching Python script
        List<int> dummyPkt = List<int>.filled(216, 0x00);
        dummyPkt[0] = EventTypes.FRAME_SOT;  // 0xFE
        dummyPkt[1] = 0x01;  // dest
        dummyPkt[2] = 0x00;  // origin
        dummyPkt[3] = EventTypes.NRM_PKT;  // 0x01
        dummyPkt[4] = 0x02;  // txp - Hardcoded to match Python script
        dummyPkt[5] = 0x01;  // rxp - Previous packet's txp
        
        // Header
        dummyPkt[6] = 0x00;  // nwk
        dummyPkt[7] = 0x00;  // nod
        dummyPkt[8] = 0x00;  // subnod
        dummyPkt[9] = 0x00;  // module
        dummyPkt[10] = 0x02;  // mode (DB_SETUP_REQ_MODE)
        dummyPkt[11] = 0x00;  // sck
        dummyPkt[12] = 0x02;  // cmd (EVENT_STATUS_CMD)
        
        // Event log data - Using 0x3E7 as dummy packet
        dummyPkt[13] = 0x04;  // Search method
        dummyPkt[14] = 0x00;  // Search number high byte
        dummyPkt[15] = 0x00;
        dummyPkt[16] = 0x03;
        dummyPkt[17] = 0xE7;  // Search number low byte (0x3E7)

        // Use hardcoded CRC values from Python script
        dummyPkt[213] = 0x95;  // CRC high byte
        dummyPkt[214] = 0x73;  // CRC low byte
        dummyPkt[215] = EventTypes.FRAME_EOT;

        _log('[TX] ${dummyPkt.map((e) => e.toRadixString(16).padLeft(2, '0').toUpperCase()).join(' ')}');
        await _port?.write(Uint8List.fromList(dummyPkt));

        _processState = EventTypes.DUMMYPKT_SEND;
        _mainProcessState = EventTypes.REQ_RSP_WAIT_STATE;
        _pkttxCnt++;
        _logEvtSearchNumber--;  // Match Python script's behavior

    } catch (e) {
        _log('[Error] Error sending dummy packet: $e');
        _resetStates();
    }
  }

  Future<void> disconnect() async {
    _processTimer?.cancel();
    _responseTimer?.cancel();
    _subscription?.cancel();
    await _port?.close();
    _port = null;
    _device = null;
    _buffer.clear();
    _panelConnectedState = EventTypes.PANEL_NOT_CONNECTED;
    _processState = EventTypes.REQ_NWK_PKT;
    _mainProcessState = EventTypes.REQ_NWK_PKT;
    _log('Disconnected from device');
  }

  void dispose() {
    _processTimer?.cancel();
    _responseTimer?.cancel();
    _subscription?.cancel();
    _port?.close();
    _logController.close();
  }

  void _scheduleAccessKeyRequest() {
    if (_accessKeyRequestScheduled) {
        _log('Access key request already scheduled, skipping');
        return;
    }
    _accessKeyRequestScheduled = true;
    Future.delayed(const Duration(milliseconds: 1670), () {  // Updated to match flow
        if (_processState == EventTypes.REQ_ACCESS_KEY) {
            _log('Sending access key request');
            _sendAccessKeyPacket();
        }
        _accessKeyRequestScheduled = false;
    });
  }

  void _scheduleDummyPacket() {
    if (_dummyPacketScheduled) {
        _log('Dummy packet already scheduled, skipping');
        return;
    }
    _dummyPacketScheduled = true;
    Future.delayed(const Duration(milliseconds: 1550), () {  // Updated to match flow
        if (_processState == EventTypes.DUMMYPKT_SEND) {
            _log('Sending dummy packet');
            _sendDummyPacket();
        }
        _dummyPacketScheduled = false;
    });
  }

  void _handleDummyPacketResponse(CommFrame frame) {
    if (frame.pktTyp == EventTypes.ACK_PKT) {
      _log('Received ACK packet');
      _processState = EventTypes.READ_EVT_LOG;
      _mainProcessState = EventTypes.READ_EVT_LOG;
      _log('Transitioning to READ_EVT_LOG state');
      _scheduleEventLogRequest();
    } else {
      _log('Invalid dummy packet response type: ${frame.pktTyp}');
      _resetStates();
    }
  }

  void _scheduleEventLogRequest() {
    Future.delayed(const Duration(milliseconds: 2360), () {  // Updated to match flow
        if (_processState == EventTypes.READ_EVT_LOG) {
            _log('Sending event log request');
            _requestEventLog();
        }
    });
  }

  Future<void> _sendEventLogRequest() async {
    try {
      // Create event log request packet exactly matching Python script
      List<int> evtLogPkt = List<int>.filled(216, 0x00);
      evtLogPkt[0] = EventTypes.FRAME_SOT;  // 0xFE
      evtLogPkt[1] = 0x01;  // dest
      evtLogPkt[2] = 0x00;  // origin
      evtLogPkt[3] = EventTypes.NRM_PKT;  // 0x01
      evtLogPkt[4] = _pkttxCnt;  // txp
      evtLogPkt[5] = _pktrxCnt;  // rxp
      
      // Header
      evtLogPkt[6] = 0x00;  // nwk
      evtLogPkt[7] = 0x00;  // nod
      evtLogPkt[8] = 0x00;  // subnod
      evtLogPkt[9] = 0x00;  // module
      evtLogPkt[10] = 0x02;  // mode (DB_SETUP_REQ_MODE)
      evtLogPkt[11] = 0x00;  // sck
      evtLogPkt[12] = 0x02;  // cmd (EVENT_STATUS_CMD)
      
      // Event log data
      evtLogPkt[13] = 0x04;  // Search method
      evtLogPkt[14] = (_logEvtSearchNumber >> 24) & 0xFF;
      evtLogPkt[15] = (_logEvtSearchNumber >> 16) & 0xFF;
      evtLogPkt[16] = (_logEvtSearchNumber >> 8) & 0xFF;
      evtLogPkt[17] = _logEvtSearchNumber & 0xFF;

      // Calculate CRC
      int crc = _calculateCRC(evtLogPkt.sublist(0, 213));
      evtLogPkt[213] = (crc >> 8) & 0xFF;
      evtLogPkt[214] = crc & 0xFF;
      evtLogPkt[215] = EventTypes.FRAME_EOT;

      _log('Sending event log request packet: ${evtLogPkt.map((e) => e.toRadixString(16).padLeft(2, '0')).join(' ')}');
      
      await _port?.write(Uint8List.fromList(evtLogPkt));
      _log('Event log request packet sent');

      if (_logEvtSearchNumber == 0) {
        _stopEvtLogRead = true;
      } else {
        _logEvtSearchNumber--;
      }

      _processState = EventTypes.READ_EVT_LOG;
      _mainProcessState = EventTypes.REQ_RSP_WAIT_STATE;
      _pkttxCnt = (_pkttxCnt + 1) & 0xFF;

    } catch (e) {
      _log('Error sending event log request: $e');
      _resetStates();
    }
  }
} 