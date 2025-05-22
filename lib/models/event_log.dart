import '../utils/timestamp_converter.dart';

class EventLog {
  final int searchMethod;
  final int searchNumber;
  final int nodeNumber;
  final int subNodeNumber;
  final int moduleNumber;
  final int eventCount;
  final int eventClass;
  final int subClass;
  final int eventType;
  final int eventStatus;
  final int eventSubType;
  final int timestamp;
  final int ioNumberType;
  final List<int> ioNumber;
  final List<int> ioData;
  final List<int> ioParam;
  final int activeEventCount;
  final int activeEventClassCount;
  final int tsOutputType;
  final int tsOutputNumber;
  final String eventText;

  EventLog({
    required this.searchMethod,
    required this.searchNumber,
    required this.nodeNumber,
    required this.subNodeNumber,
    required this.moduleNumber,
    required this.eventCount,
    required this.eventClass,
    required this.subClass,
    required this.eventType,
    required this.eventStatus,
    required this.eventSubType,
    required this.timestamp,
    required this.ioNumberType,
    required this.ioNumber,
    required this.ioData,
    required this.ioParam,
    required this.activeEventCount,
    required this.activeEventClassCount,
    required this.tsOutputType,
    required this.tsOutputNumber,
    required this.eventText,
  });

  factory EventLog.fromFrame(List<int> frameData) {
    // Extract fields from frame data exactly matching Python script
    int searchMethod = frameData[13];
    int searchNumber = (frameData[14] << 24) | (frameData[15] << 16) | (frameData[16] << 8) | frameData[17];
    int nodeNumber = frameData[18];
    int subNodeNumber = frameData[19];
    int moduleNumber = frameData[20];
    int eventCount = (frameData[21] << 24) | (frameData[22] << 16) | (frameData[23] << 8) | frameData[24];
    int eventClass = frameData[25];
    int subClass = frameData[26];
    int eventType = frameData[27];
    int eventStatus = frameData[28];
    int eventSubType = frameData[29];
    int timestamp = (frameData[30] << 24) | (frameData[31] << 16) | (frameData[32] << 8) | frameData[33];
    int ioNumberType = frameData[34];
    List<int> ioNumber = frameData.sublist(35, 37);
    List<int> ioData = frameData.sublist(37, 47);
    List<int> ioParam = frameData.sublist(47, 50);
    int activeEventCount = (frameData[50] << 24) | (frameData[51] << 16) | (frameData[52] << 8) | frameData[53];
    int activeEventClassCount = (frameData[54] << 24) | (frameData[55] << 16) | (frameData[56] << 8) | frameData[57];
    int tsOutputType = frameData[58];
    int tsOutputNumber = frameData[59];

    // Extract event text
    int textLength = frameData[60];
    String eventText = '';
    if (textLength > 0) {
      List<int> textBytes = frameData.sublist(61, 61 + textLength);
      eventText = String.fromCharCodes(textBytes);
    }

    return EventLog(
      searchMethod: searchMethod,
      searchNumber: searchNumber,
      nodeNumber: nodeNumber,
      subNodeNumber: subNodeNumber,
      moduleNumber: moduleNumber,
      eventCount: eventCount,
      eventClass: eventClass,
      subClass: subClass,
      eventType: eventType,
      eventStatus: eventStatus,
      eventSubType: eventSubType,
      timestamp: timestamp,
      ioNumberType: ioNumberType,
      ioNumber: ioNumber,
      ioData: ioData,
      ioParam: ioParam,
      activeEventCount: activeEventCount,
      activeEventClassCount: activeEventClassCount,
      tsOutputType: tsOutputType,
      tsOutputNumber: tsOutputNumber,
      eventText: eventText,
    );
  }

  String getFormattedDateTime() {
    return TimestampConverter.formatTimestamp(timestamp);
  }

  String getEventStatusText() {
    switch (eventStatus) {
      case 0: return 'Active';
      case 1: return 'Cleared';
      case 2: return 'Logged';
      default: return 'Unknown';
    }
  }

  String getEventClassText() {
    switch (eventClass) {
      case 1: return 'System';
      case 2: return 'Action';
      case 3: return 'Alarm';
      case 4: return 'Status';
      case 5: return 'Diagnostic';
      case 6: return 'Network';
      default: return 'Unknown';
    }
  }

  String getEventTypeText() {
    // TODO: Implement event type mapping
    return 'Unknown';
  }

  @override
  String toString() {
    return '''
EVENT-ID    PANEL NO.   L-BUS NO.   MODULE NO.  EVTLOG DATE     EVTLOG TIME     EVENT STATUS      EVENT CLASS         EVENT TYPE           EVENT                       IDENTIFIER                  TEXT
${searchNumber.toString().padRight(12)} ${nodeNumber.toString().padRight(12)} ${subNodeNumber.toString().padRight(12)} ${moduleNumber.toString().padRight(12)} ${getFormattedDateTime().padRight(18)} ${getEventStatusText().padRight(18)} ${getEventClassText().padRight(18)} ${getEventTypeText().padRight(18)} ${eventText.padRight(28)} -                           ${eventText.isEmpty ? 'NO-TEXT' : eventText}
''';
  }
} 