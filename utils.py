#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime


def getTimestamp():
    """
    Utility function to get a nicely formatted timestamp
    :return: Returns date and time in the following format "DD/MM [HH:MM]"
    """
    dt = str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day) + ' '
    hr = str(datetime.datetime.now().hour) if len(str(datetime.datetime.now().hour)) > 1 else '0' + str(datetime.datetime.now().hour)
    min = str(datetime.datetime.now().minute) if len(str(datetime.datetime.now().minute)) > 1 else '0' + str(datetime.datetime.now().minute)
    t = '[' + hr + ':' + min + '] '
    return dt + t


def clamp_int(value, minimum, maximum):
    """
    Clamp integer between 2 values
    :param value: Current value
    :param minimum: Minimum value
    :param maximum: Maximum value
    :return: Current value, clamped to between min and max
    """
    if value < minimum:
        value = minimum
    elif value > maximum:
        value = maximum
    return value

def make_discord_timestamp(value):
    """
    Build a Discord timestamp from a string or date object
    This is a Unix timestamp that displays a datetime to a Discord user in their localised timezone.
    """
    if isinstance(value, datetime.datetime):
        return f"<t:{int(value.timestamp())}:F>"
    if isinstance(value, str):
        return f"<t:{int(datetime.datetime.strptime(value, '%b %d %Y %H:%M').timestamp())}:F>"
