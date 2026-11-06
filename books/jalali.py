"""Minimal Gregorian → Jalali conversion, used only for form defaults.

Pure Python on purpose: the project adds no calendar package (AGENTS.md).
Algorithm: the widely used day-count method (as in jalaali-js).
"""

from django.utils import timezone

_GREGORIAN_DAYS_BEFORE_MONTH = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)


def gregorian_to_jalali(gy, gm, gd):
    """Return (jalali_year, jalali_month, jalali_day) for a Gregorian date."""
    if gy > 1600:
        jy, gy = 979, gy - 1600
    else:
        jy, gy = 0, gy - 621
    gy2 = gy + 1 if gm > 2 else gy
    days = (
        365 * gy
        + (gy2 + 3) // 4
        - (gy2 + 99) // 100
        + (gy2 + 399) // 400
        - 80
        + gd
        + _GREGORIAN_DAYS_BEFORE_MONTH[gm - 1]
    )
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + days // 31, 1 + days % 31
    else:
        jm, jd = 7 + (days - 186) // 30, 1 + (days - 186) % 30
    return jy, jm, jd


def today_jalali():
    """Return (year, month) of today's date in the project time zone."""
    today = timezone.localdate()
    jy, jm, _ = gregorian_to_jalali(today.year, today.month, today.day)
    return jy, jm
