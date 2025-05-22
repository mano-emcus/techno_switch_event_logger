import 'dart:typed_data';
import '../models/event_types.dart';

class CommHeader {
  int nwk;
  int nod;
  int subnod;
  int module;
  int mode;
  int sck;
  int cmd;

  CommHeader({
    this.nwk = 0x00,
    this.nod = 0x00,
    this.subnod = 0x00,
    this.module = 0x00,
    this.mode = 0x00,
    this.sck = 0x00,
    this.cmd = 0x00,
  });

  List<int> toBytes() {
    return [nwk, nod, subnod, module, mode, sck, cmd];
  }

  factory CommHeader.fromBytes(List<int> bytes) {
    return CommHeader(
      nwk: bytes[0],
      nod: bytes[1],
      subnod: bytes[2],
      module: bytes[3],
      mode: bytes[4],
      sck: bytes[5],
      cmd: bytes[6],
    );
  }
}

class CommData {
  CommHeader header;
  List<int> data;

  CommData({
    CommHeader? header,
    List<int>? data,
  })  : header = header ?? CommHeader(),
        data = data ?? List<int>.filled(EventTypes.FRAME_PAYLOAD_SIZE, 0x00);

  List<int> toBytes() {
    return [...header.toBytes(), ...data];
  }

  factory CommData.fromBytes(List<int> bytes) {
    if (bytes.length < EventTypes.FRAME_HEADER_SIZE) {
      throw Exception('Invalid data length for CommData header: ${bytes.length} bytes');
    }

    // Calculate the expected data length (total length - header size)
    int dataLength = bytes.length - EventTypes.FRAME_HEADER_SIZE;
    if (dataLength > EventTypes.FRAME_PAYLOAD_SIZE) {
      throw Exception('Data length exceeds maximum payload size: $dataLength bytes');
    }

    // Create a fixed-size data array and copy the available data
    List<int> fullData = List<int>.filled(EventTypes.FRAME_PAYLOAD_SIZE, 0x00);
    for (int i = 0; i < dataLength; i++) {
      fullData[i] = bytes[EventTypes.FRAME_HEADER_SIZE + i];
    }

    return CommData(
      header: CommHeader.fromBytes(bytes.sublist(0, EventTypes.FRAME_HEADER_SIZE)),
      data: fullData,
    );
  }
}

class CommFrame {
  int sot;
  int dest;
  int origin;
  int pktTyp;
  int txp;
  int rxp;
  CommData payload;
  int crc;
  int eot;

  CommFrame({
    this.sot = EventTypes.FRAME_SOT,
    this.dest = 0x00,
    this.origin = 0x00,
    this.pktTyp = 0x00,
    this.txp = 0x00,
    this.rxp = 0x00,
    CommData? payload,
    this.crc = 0x0000,
    this.eot = EventTypes.FRAME_EOT,
  }) : payload = payload ?? CommData();

  int calculateCRC() {
    List<int> data = [
      sot,
      dest,
      origin,
      pktTyp,
      txp,
      rxp,
      ...payload.toBytes(),
    ];
    
    // Fletcher checksum implementation exactly matching Python script
    int sum1 = 0;
    int sum2 = 0;
    
    // Process each byte
    for (int i = 0; i < data.length; i++) {
      sum1 = (sum1 + data[i]) % 255;
      sum2 = (sum2 + sum1) % 255;
    }
    
    // Calculate final checksum exactly as in Python
    int chk1 = (255 - ((sum1 + sum2) % 255)) & 0xFF;
    int chk2 = (255 - ((sum1 + chk1) % 255)) & 0xFF;
    
    // Return combined checksum with bytes in correct order
    return (chk1 << 8) | chk2;
  }

  Uint8List toBytes() {
    // Calculate CRC before creating frame bytes
    crc = calculateCRC();
    
    List<int> frameBytes = [
      sot,
      dest,
      origin,
      pktTyp,
      txp,
      rxp,
      ...payload.toBytes(),
      (crc >> 8) & 0xFF,  // CRC high byte
      crc & 0xFF,         // CRC low byte
      eot,
    ];
    
    // Debug log
    print('Frame bytes: ${frameBytes.map((e) => e.toRadixString(16).padLeft(2, '0')).join(' ')}');
    
    return Uint8List.fromList(frameBytes);
  }

  factory CommFrame.fromBytes(List<int> bytes) {
    if (bytes.length != EventTypes.COMM_EACH_FRAME_SIZE) {
      throw Exception('Invalid frame size: ${bytes.length} bytes, expected: ${EventTypes.COMM_EACH_FRAME_SIZE}');
    }
    
    if (bytes[0] != EventTypes.FRAME_SOT || bytes[bytes.length - 1] != EventTypes.FRAME_EOT) {
      throw Exception('Invalid frame markers: SOT=${bytes[0].toRadixString(16)}, EOT=${bytes[bytes.length - 1].toRadixString(16)}');
    }

    // Extract CRC bytes in correct order
    int receivedCrc = (bytes[bytes.length - 3] << 8) | bytes[bytes.length - 2];
    
    // Create frame without CRC validation first
    CommFrame frame = CommFrame(
      sot: bytes[0],
      dest: bytes[1],
      origin: bytes[2],
      pktTyp: bytes[3],
      txp: bytes[4],
      rxp: bytes[5],
      payload: CommData.fromBytes(bytes.sublist(6, bytes.length - 3)),
      crc: receivedCrc,
      eot: bytes[bytes.length - 1],
    );
    
    // Calculate and validate CRC
    int calculatedCrc = frame.calculateCRC();
    if (calculatedCrc != receivedCrc) {
      print('Warning: CRC mismatch - calculated=0x${calculatedCrc.toRadixString(16)}, received=0x${receivedCrc.toRadixString(16)}');
      // Don't throw exception, just warn - some devices might not use CRC
    }
    
    return frame;
  }
} 