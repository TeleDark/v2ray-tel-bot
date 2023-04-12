import re
import json
from keys import *
from datetime import datetime
from persiantools.jdatetime import JalaliDateTime

ONE_KB = 1024
ONE_MB = ONE_KB * 1024
ONE_GB = ONE_MB * 1024
ONE_TB = ONE_GB * 1024
ONE_PB = ONE_TB * 1024

# convert 1 Gigabytes to Bytes
mb_or_gb = 1073741824

# read data from json file
def read_json():
    with open(json_file) as f:
        return json.load(f)

# checking the amount of traffic
def sizeFormat(size):
    if (size < ONE_KB):
        return "{:.0f}".format(size) + " B"
    elif (size < ONE_MB):
        return "{:.2f}".format(size / ONE_KB) + " KB"
    elif (size < ONE_GB):
        return "{:.2f}".format(size / ONE_MB) + " MB"
    elif (size < ONE_TB):
        return "{:.2f}".format(size / ONE_GB) + " GB"
    elif (size < ONE_PB):
        return "{:.2f}".format(size / ONE_TB) + " TB"
    else:
        return "{:.2f}".format(size / ONE_PB) + " PB"

# checking the amount of traffic uploaded
def check_up(user_index, data):
    return sizeFormat(data[user_index]['up'])

# checking the amount of downloaded
def check_down(user_index, data):
    return sizeFormat(data[user_index]['down'])


def check_used(user_index, data):
    return sizeFormat(data[user_index]['down'] + data[user_index]['up'])


def status(user_index, data):
    return "✅ فعال" if data[user_index]['enable'] else "⛔️غیرفعال"

# checking the total amount of traffic
def check_total(user_index, data):
    total = data[user_index]['total']
    if total == 0:
        return '♾'
    return sizeFormat(total)


def extract_time(time_rem):
    try:
        if 'day' not in time_rem:
            result = list(re.findall(
                r"(\d{1,2}):(\d{1,2}):", time_rem)[0])
        else:
            result = list(re.findall(
                r"^(?!-)(\d*) day.?, (\d{1,2}):(\d{1,2}):", time_rem)[0])
    except IndexError:
        return 'اتمام سرویس'
        
    if len(result) == 3:
        day, hour, minute = result
    else: 
        hour, minute = result
        day = ''
    if day != '':
        day = day + ' روز و '

    if hour != '0':
        hour = hour + ' ساعت و '
    elif hour == '0':
        hour = ''

    minute = minute + ' دقیقه'
    rem_time = day + hour + minute
    return rem_time

# checking the expiry Time
def check_expiryTime(user_index, data):
    time_stamp = data[user_index]['expiryTime']
    if time_stamp == 0:
        return ['♾', 'زمان ♾']
    
    s = time_stamp / 1000.0

    timestamp_to_strtime = datetime.fromtimestamp(
        s).strftime('%Y-%m-%d %H:%M:%S')

    date = datetime.strptime(timestamp_to_strtime, "%Y-%m-%d %H:%M:%S")
    date_time_rem = str(date - datetime.now())

    time_rem = extract_time(date_time_rem)
    
    jdate = JalaliDateTime.to_jalali(
        datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)).strftime("%Y-%m-%d %H:%M:%S")

    return [time_rem, jdate]

# get account info based on uuid
def account_info(uuid):
    data = read_json()
    try:
        settings_data = str([data[i]['settings'] for i in range(len(data))])
        user_index = re.findall(".{8}-.{4}-.{4}-.{4}-.{12}", settings_data).index(uuid)
        found = True

    except ValueError:
        return 'not found'
    
    if found:
        return [status(user_index, data), check_up(user_index, data), check_down(user_index, data), check_used(user_index, data), check_total(user_index, data), check_expiryTime(user_index, data)]