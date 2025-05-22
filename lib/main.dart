import 'package:flutter/material.dart';
import 'package:usb_serial/usb_serial.dart';
import 'services/usb_serial_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Event Logger',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const EventLoggerScreen(),
    );
  }
}

class EventLoggerScreen extends StatefulWidget {
  const EventLoggerScreen({super.key});

  @override
  State<EventLoggerScreen> createState() => _EventLoggerScreenState();
}

class _EventLoggerScreenState extends State<EventLoggerScreen> {
  final UsbSerialService _serialService = UsbSerialService();
  final List<String> _logs = [];
  List<UsbDevice> _devices = [];
  UsbDevice? _selectedDevice;
  bool _isConnected = false;
  bool _isLoading = false;
  bool _headerPrinted = false;

  @override
  void initState() {
    super.initState();
    _initUsbSerial();
    _serialService.logStream.listen(_onLogReceived);
    UsbSerial.usbEventStream?.listen((UsbEvent event) {
      _initUsbSerial();
    });
  }

  void _onLogReceived(String log) {
    // Print header only once when we start receiving event logs
    if (!_headerPrinted && log.contains('EVENT-ID')) {
      _headerPrinted = true;
    }

    // Only display formatted event logs and header
    if (!log.contains('[TX]') && !log.contains('[RX]')) {
      setState(() {
        _logs.insert(0, log); // Add new logs at the top
        if (_logs.length > 1000) {
          _logs.removeLast();
        }
      });
    }
  }

  Future<void> _initUsbSerial() async {
    try {
      _devices = await _serialService.getDevices();
      setState(() {});
    } catch (e) {
      _onLogReceived('Error getting USB devices: $e');
    }
  }

  Future<void> _connectToDevice(UsbDevice device) async {
    setState(() {
      _isLoading = true;
      _headerPrinted = false; // Reset header flag on new connection
    });

    try {
      bool connected = await _serialService.connect(device);
      setState(() {
        _selectedDevice = connected ? device : null;
        _isConnected = connected;
        _isLoading = false;
      });

      if (connected) {
        _serialService.requestNetworkPacket();
      }
    } catch (e) {
      _onLogReceived('Error connecting to device: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _disconnect() async {
    setState(() {
      _isLoading = true;
      _headerPrinted = false; // Reset header flag on disconnect
    });

    try {
      await _serialService.disconnect();
      setState(() {
        _selectedDevice = null;
        _isConnected = false;
        _isLoading = false;
      });
    } catch (e) {
      _onLogReceived('Error disconnecting: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  void dispose() {
    _serialService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Event Logger'),
        actions: [
          if (_devices.isNotEmpty && !_isLoading)
            DropdownButton<UsbDevice>(
              value: _selectedDevice,
              hint: const Text('Select Device'),
              items: _devices.map((device) {
                return DropdownMenuItem(
                  value: device,
                  child: Text(device.productName ?? 'Unknown Device'),
                );
              }).toList(),
              onChanged: _isConnected ? null : (device) {
                if (device != null) {
                  _connectToDevice(device);
                }
              },
            ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: CircularProgressIndicator(),
            ),
          if (_isConnected && !_isLoading)
            IconButton(
              icon: const Icon(Icons.usb_off),
              onPressed: _disconnect,
            ),
        ],
      ),
      body: Column(
        children: [
          if (_devices.isEmpty)
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text('No USB devices found. Please connect a device.'),
            ),
          Expanded(
            child: ListView.builder(
              reverse: true, // Show newest logs at the top
              itemCount: _logs.length,
              itemBuilder: (context, index) {
                final log = _logs[index];
                final isHeader = log.contains('EVENT-ID');
                
                return isHeader ? Card(
                  margin: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
                  color: isHeader ? Colors.grey[200] : Colors.white,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: SelectableText(
                      log,
                      style: TextStyle(
                        fontFamily: 'monospace',
                        fontWeight: isHeader ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ),
                ) : const SizedBox();
              },
            ),
          ),
        ],
      ),
    );
  }
}
