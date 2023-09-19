import re
import json
import base64
from keys import *
from datetime import datetime
from persiantools.jdatetime import JalaliDateTime

ONE_KB = 1024
ONE_MB = ONE_KB * 1024
ONE_GB = ONE_MB * 1024
ONE_TB = ONE_GB * 1024
ONE_PB = ONE_TB * 1024

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

def get_account_name(user_index, data):
    return data[user_index]['email']

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

def traffic_remaining(user_index, data):
    data = data[user_index]
    total = data['total']
    if total != 0:
        remaining = total - (data['down'] + data['up'])
        if remaining <= 0:
            return '⛔️'
        
        return sizeFormat(remaining)
    
    return '♾'

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


def parseVmess(vmesslink):
    vmscheme = 'vmess://'
    if vmesslink.startswith(vmscheme):
        bs = vmesslink[8:]
        blen = len(bs)
        if blen % 4 > 0:
            bs += "=" * (4 - blen % 4)

        vms = base64.b64decode(bs).decode()
        return vms

def parseShadowsocks(sslink):
    data = re.findall(r"^ss://(.+)@.+$", sslink)[0]
    len_data = len(data)
    if len_data % 4 > 0:
        data += '=' * (4 - len_data % 4)
    
    decoded_data = base64.b64decode(data).decode()
    password = decoded_data.split(':')[-1]
    return password

# get account info based on uuid
def account_info(id):
    data = read_json()
    if re.match(r"^vmess://.*", id):
        id = re.findall(r".{8}-.{4}-.{4}-.{4}-.{12}", parseVmess(id))[0]
        query = f"'id': '{id}'"
    
    elif re.match(r"^vless://.*@.*", id):
        id = re.findall(r"^vless://(.{8}-.{4}-.{4}-.{4}-.{12})@", id)[0]
        query = f"'id': '{id}'"
    
    elif re.match(r"^ss://.*@.*", id):
        id = parseShadowsocks(id)
        query = f"'password': '{id}'"
    
    elif re.match(r"^trojan://.*@.*", id):
        id = re.findall(r"^trojan://(.+)@.+", id)[0]
        query = f"'password': '{id}'"
    
    elif re.match(r"^.{8}-.{4}-.{4}-.{4}-.{12}$", id):
        query = f"'id': '{id}'"
    
    else:
        query = f"'email': '{id}'"
    
    found = False

    for conf in data:
        if query in conf["settings"]:
            user_index = data.index(conf)
            found = True
            break
    
    if found:
        return [status(user_index, data), get_account_name(user_index, data), check_up(user_index, data), check_down(user_index, data), check_used(user_index, data), check_total(user_index, data), traffic_remaining(user_index, data), check_expiryTime(user_index, data)]
    
    else:
        return 'not found'
