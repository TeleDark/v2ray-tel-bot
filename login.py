import re
import requests
import json
from keys import *

url_login = "login"
url_lists = "xui/inbound/list"

# write data in json file
def write_json(json_data):
    with open(json_file, 'a') as f:
        json.dump(json_data, f)


# login to all panels and save data
def login():
    lists = []
    new_list = []

    for panel in panels:
        if panel['url'][-1] != '/':
            panel['url']+='/'
        
        try:
            panel_name = re.findall(r"http.?://(.*):", panel['url'])[0]
        except IndexError:
            print(f"{panel['url']} : The URL structure is incorrect")
            break
            
        payload = {
            "username": panel['username'],
            "password": panel['password']
        }

        session = requests.Session()
        try: 
            response = session.post(panel['url'] + url_login, data=payload)
        except (requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
            print(f"{panel['url']} : incorrect URL or port number")
            break
        
        if response.json()['success']:
            data_list = session.post(panel['url'] + url_lists).json()['obj']
            if not data_list:
                print(panel_name,': is empty')
                continue

            if 'clientStats' in data_list[0]:
                """ English panel """

                for i in range(len(data_list)):
                    prev = ''
                    try:
                        client_emails = [data_list[i]['clientStats'][j]['email'] for j in range(len(data_list[i]['clientStats']))]
                        setting_emails = [json.loads(data_list[i]['settings'])['clients'][j]['email'] for j in range(len(json.loads(data_list[i]['settings'])['clients']))]
                        
                        try:
                            k = 0
                            for j in range(len(client_emails)):
                                if client_emails[j] not in setting_emails:
                                    del data_list[i]['clientStats'][j-k]
                                    k += 1
                        except Exception as e:
                            print(e)

                        inbound = data_list[i]['clientStats']
                        setting = json.loads(data_list[i]['settings'])[
                            'clients']
                        sorted_inbound = sorted(inbound, key=lambda x: [
                            d['email'] for d in setting].index(x['email']))
                        data_list[i]['clientStats'] = sorted_inbound

                        for j in range(len(data_list[i]['clientStats'])):

                            if prev == json.loads(data_list[i]['settings'])['clients'][j]['id']:
                                break
                            prev = json.loads(data_list[i]['settings'])[
                                'clients'][j]['id']
                            
                            data_list[i]['clientStats'][j]['settings'] = str(
                                json.loads(data_list[i]['settings'])['clients'][j])
                            new_list.append(data_list[i]['clientStats'][j])

                    except Exception as e:
                        print(e)

                data_list = new_list    
            else:
                for i in range(len(data_list)):
                    data_list[i].pop('streamSettings')
                    data_list[i].pop('sniffing')
                    data_list[i].pop('tag')
                    data_list[i]['settings'] = str(json.loads(
                        data_list[i]['settings'])['clients'][0])[:-1] + ", 'email': '" + data_list[i].pop('remark') + "', "

            lists.extend(data_list)
            print(f"{panel_name} : login successful")
        else:
            print(f"{panel_name} : wrong Username or Password")
    
    open(json_file, 'w').close()
    write_json(lists)


if __name__ == '__main__':
    login()
