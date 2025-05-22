import 'package:collection/collection.dart';

class TimestampConverter {
  static bool isLeapYear(int year) {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
  }

  static int getMaxDayOfMonth(int year, int month) {
    const List<int> daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    if (month == 2 && isLeapYear(year)) {
      return 29;
    }
    return daysInMonth[month - 1];
  }

  static int getMaxDayOfYear(int year) {
    return isLeapYear(year) ? 366 : 365;
  }

  static int calcYearDays(int year) {
    int days = 0;
    for (int y = 1970; y < year; y++) {
      days += getMaxDayOfYear(y);
    }
    return days;
  }

  static int calcDays(DateTime date) {
    int days = calcYearDays(date.year);
    for (int m = 1; m < date.month; m++) {
      days += getMaxDayOfMonth(date.year, m);
    }
    days += date.day - 1;
    return days;
  }

  static int calcDayOfWeek(DateTime date) {
    return date.weekday % 7; // Convert to 0-6 range where 0 is Sunday
  }

  static DateTime fromTimestamp(int timestamp) {
    // Convert timestamp to DateTime using the same logic as Python script
    int seconds = timestamp & 0x3F; // 6 bits
    int minutes = (timestamp >> 6) & 0x3F; // 6 bits
    int hours = (timestamp >> 12) & 0x1F; // 5 bits
    int day = (timestamp >> 17) & 0x1F; // 5 bits
    int month = (timestamp >> 22) & 0x0F; // 4 bits
    int year = ((timestamp >> 26) & 0x3F) + 2000; // 6 bits + 2000

    // Validate and adjust values
    if (month < 1) month = 1;
    if (month > 12) month = 12;
    if (day < 1) day = 1;
    if (day > getMaxDayOfMonth(year, month)) {
      day = getMaxDayOfMonth(year, month);
    }
    if (hours > 23) hours = 23;
    if (minutes > 59) minutes = 59;
    if (seconds > 59) seconds = 59;

    return DateTime(year, month, day, hours, minutes, seconds);
  }

  static String formatDateTime(DateTime dateTime) {
    String date = '${dateTime.day.toString().padLeft(2, '0')}/${dateTime.month.toString().padLeft(2, '0')}/${dateTime.year}';
    String time = '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}:${dateTime.second.toString().padLeft(2, '0')}';
    return '$date $time';
  }

  static String formatTimestamp(int timestamp) {
    DateTime dateTime = fromTimestamp(timestamp);
    return formatDateTime(dateTime);
  }
} 