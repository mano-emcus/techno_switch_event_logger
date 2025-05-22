# Techno Switch Rhino 103 Event Logger

A Flutter application for reading event logs from Techno Switch Rhino 103 controller via USB serial communication.

## Features

- Connect to Techno Switch Rhino 103 controller via USB
- Read and display event logs in real-time
- Support for various event types and statuses
- Clean and modern Material Design UI

## Setup

1. Install Flutter (if not already installed)
2. Clone this repository
3. Run `flutter pub get` to install dependencies
4. Connect your Techno Switch Rhino 103 controller to your Android device via USB
5. Run the app using `flutter run`

## Android Setup

Add the following to your `android/app/src/main/AndroidManifest.xml` file inside the `<application>` tag:

```xml
<intent-filter>
    <action android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED" />
</intent-filter>
<meta-data android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED"
    android:resource="@xml/device_filter" />
```

Create a file `android/app/src/main/res/xml/device_filter.xml` with the following content:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Add your device's vendor ID and product ID here -->
    <usb-device vendor-id="1027" product-id="24577" />
</resources>
```

## Usage

1. Launch the application
2. Select your device from the dropdown menu in the app bar
3. The app will automatically start reading event logs
4. Event logs will be displayed in a scrollable list
5. Click the USB disconnect icon to disconnect from the device

## Dependencies

- Flutter SDK
- usb_serial: ^0.5.2

## License

MIT License
