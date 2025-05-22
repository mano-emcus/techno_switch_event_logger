
# def tools_fletcher_checksum(p_buffer):
#     length = len(p_buffer)
#     checksum = 0

#     if length > 0:
#         sum1 = 0
#         sum2 = 0
#         for i in range(length):
#             sum1 = (sum1 + p_buffer[i]) % 255
#             sum2 = (sum2 + sum1) % 255

#         chk1 = (255 - ((sum1 + sum2) % 255)) & 0xFF
#         chk2 = (255 - ((sum1 + chk1) % 255)) & 0xFF

#         checksum = (chk1 << 8) | chk2

#     return checksum


# hex_string= "FE 01 00 01 05 04 00 00 00 00 02 00 0D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"


# # 🧠 Convert to list of integers
# byte_list = [int(byte, 16) for byte in hex_string.strip().split()]


# checksum = tools_fletcher_checksum(byte_list)
# print(f"Fletcher Checksum: 0x{checksum:04X}")










# Converted from the provided C code into Python

from dataclasses import dataclass

@dataclass
class DateTime:
    Year: int
    Month: int
    Day: int
    Hour: int
    Minute: int
    Second: int
    DayOfWeek: int

ClockTimeStart = DateTime(1970, 1, 1, 0, 0, 0, 3)

MAX_DAYS_NON_LEAP_YEAR = 365
MAX_DAYS_LEAP_YEAR = 366

MIN_MONTH = 1
MAX_MONTH = 12

MAX_DAY_OF_MONTH_NON_LEAP_YEAR = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MAX_DAY_OF_MONTH_LEAP_YEAR     = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def is_leap_year(year):
    return (year % 400 == 0) or ((year % 4 == 0) and (year % 100 != 0))

def RTC_MaxDayOfMonth(year, month):
    if MIN_MONTH <= month <= MAX_MONTH:
        if is_leap_year(year):
            return MAX_DAY_OF_MONTH_LEAP_YEAR[month - 1]
        else:
            return MAX_DAY_OF_MONTH_NON_LEAP_YEAR[month - 1]
    return 0

def RTC_MaxDayOfYear(year):
    return MAX_DAYS_LEAP_YEAR if is_leap_year(year) else MAX_DAYS_NON_LEAP_YEAR

def CalcYearDays(year):
    d = 0
    y = ClockTimeStart.Year
    while y < year:
        d += RTC_MaxDayOfYear(y)
        y += 1
    return d

def CalcDays(pTime):
    d = CalcYearDays(pTime.Year)
    for m in range(1, pTime.Month):
        d += RTC_MaxDayOfMonth(pTime.Year, m)
    d += pTime.Day
    return d

def CalcDayOfWeek(pTime):
    return (CalcDays(pTime) - 1 + ClockTimeStart.DayOfWeek) % 7

def CLOCK_TimeFromTimeStamp(timestamp):
    pTime = DateTime(0, 0, 0, 0, 0, 0, 0)
    if timestamp > 0:
        d = timestamp // (24 * 60 * 60)
        s = timestamp % (24 * 60 * 60)

        pTime.Year = d // 365 + ClockTimeStart.Year
        if CalcYearDays(pTime.Year) > d:
            pTime.Year -= 1

        pTime.Month = 1
        d -= CalcYearDays(pTime.Year)
        dm = RTC_MaxDayOfMonth(pTime.Year, pTime.Month)

        while d > dm:
            pTime.Month += 1
            d -= dm
            dm = RTC_MaxDayOfMonth(pTime.Year, pTime.Month)

        pTime.Day = d

        pTime.Hour = s // 3600
        s -= pTime.Hour * 3600

        pTime.Minute = s // 60
        s -= pTime.Minute * 60

        pTime.Second = s

        pTime.DayOfWeek = CalcDayOfWeek(pTime)

    return pTime

# # Example usage
# timestamp_curr = 0x681DF257
# EventTime = CLOCK_TimeFromTimeStamp(timestamp_curr)

# print(f"Date: {EventTime.Day}/{EventTime.Month}/{EventTime.Year}")
# print(f"Time (HH:MM:SS): {EventTime.Hour}:{EventTime.Minute}:{EventTime.Second} - Day of Week: {EventTime.DayOfWeek}")

