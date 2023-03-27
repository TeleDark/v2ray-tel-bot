import re
import json
from datetime import datetime
from persiantools.jdatetime import JalaliDateTime

#json file
json_file = "accounts_info.json"

# convert 1 Gigabytes to Bytes
mb_or_gb = 1073741824

# read data from json file
def read_json():
    with open(json_file) as f:
        return json.load(f)
    
data = read_json()


# convert traffic consumed to gigabytes 
def gb(traffic_usage):
    gibibytes = traffic_usage / (1024 ** 3)
    return str(round(gibibytes, 2)) + "GB"

# convert traffic consumed to megabyte
def mb(traffic_usage):
    mib = traffic_usage / 1048.576
    return str(round(mib / 10)/100) + "MB"

# checking the amount of traffic based on gigabytes and megabytes
def check_mb_or_gb(traffic):
    if traffic >= mb_or_gb:
        return gb(traffic)
    else:
        return mb(traffic)

# checking the amount of traffic uploaded
def check_up(user_index, data):
    return check_mb_or_gb(data[user_index]['up'])

# checking the amount of downloaded
def check_down(user_index, data):
    return check_mb_or_gb(data[user_index]['down'])

# checking the total amount of traffic
def check_total(user_index, data):
    total = data[user_index]['total']
    if total == 0:
        return '♾'
    return check_mb_or_gb(total)

# checking the expiry Time
def check_expiryTime(user_index, data):
    time_stamp = data[user_index]['expiryTime']
    if time_stamp == 0:
        return 'زمان ♾'
    
    s = time_stamp / 1000.0

    timestamp_to_strtime = datetime.fromtimestamp(
        s).strftime('%Y-%m-%d %H:%M:%S')

    date = datetime.strptime(timestamp_to_strtime, "%Y-%m-%d %H:%M:%S")
    jdate = JalaliDateTime.to_jalali(
        datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)).strftime("%Y-%m-%d %H:%M:%S")

    return jdate

# get account info based on uuid
def account_info(uuid):
    try:
        settings_data = str([data[i]['settings'] for i in range(len(data))])
        user_index = re.findall(".{8}-.{4}-.{4}-.{4}-.{12}", settings_data).index(uuid)
        found = True

    except ValueError:
        return 'not found'
    
    if found:
        return [check_up(user_index, data), check_down(user_index, data), check_total(user_index, data), check_expiryTime(user_index, data)]

