import re
import requests
import json
import pickle
from keys import *

url_login = "login"
url_lists = "xui/inbound/list"
url_sanaei = "panel/inbound/list"

# write data in json file
def write_json(json_data):
    with open(json_file, 'a') as f:
        json.dump(json_data, f)

# save login session in pickle file
def write_pickle(pickle_data):
    with open(pickle_file, 'wb') as f:
        pickle.dump(pickle_data, f)

def file_exists(file_path):
    return os.path.exists(file_path)

def is_file_empty(file_path):
    return file_exists(file_path) and os.stat(file_path).st_size == 0


def get_data_from_panels():
    panels_data = {}
    cookies = {}
    
    if not file_exists(pickle_file):
        open(pickle_file, 'w').close()

    elif not is_file_empty(pickle_file):
        try:
            with open(pickle_file, 'rb') as f:
                cookies = pickle.load(f)
        except:
            open(pickle_file, 'w').close()

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
        if panel_name in cookies:
            session.cookies.update(cookies[panel_name])
            try:
                panel_data = session.post(panel['url'] + url_lists)
                if panel_data.status_code != 404 and len(panel_data.content) > 0:
                    panels_data[panel_name] = panel_data.json()['obj']
                else: 
                    panels_data[panel_name] = session.post(panel['url'] + url_sanaei).json()['obj']
            except requests.exceptions.JSONDecodeError:
                get_data_from_panels()
        else:
            try:
                response = session.post(panel['url'] + url_login, data=payload)
                if response.status_code == 404:
                    print(f"{panel_name} : Are you sure your panel doesn't have a path address?")
                    continue
                elif len(response.content) == 0:
                    print(f"{panel_name} : Are you sure your panel doesn't have a path address?")
                    continue
                elif not response.json()['success']:
                    print(f"{panel_name} : wrong Username or Password")
                    continue
                
            except (requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
                print(f"{panel['url']} : incorrect URL or port number")
                continue

            cookies[panel_name] = response.cookies.get_dict()

            panel_data = session.post(panel['url'] + url_lists)
            if panel_data.status_code != 404 and len(panel_data.content) > 0:
                panels_data[panel_name] = panel_data.json()['obj']
            else: 
                panels_data[panel_name] = session.post(panel['url'] + url_sanaei).json()['obj']
    write_pickle(cookies)
    return panels_data

# save data
def save_accounts_to_json():
    lists = []
    new_list = []
    panels_data = get_data_from_panels()

    for panel_name, data_list in panels_data.items():

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

                        if prev == json.loads(data_list[i]['settings'])['clients'][j]:
                            break
                        prev = json.loads(data_list[i]['settings'])[
                            'clients'][j]
                        
                        data_list[i]['clientStats'][j]['settings'] = str(
                            json.loads(data_list[i]['settings'])['clients'][j])
                        new_list.append(data_list[i]['clientStats'][j])

                except Exception as e:
                    continue

            data_list = new_list

        elif 'clientInfo' in data_list[0]:
            """ kafka panel """

            for i in range(len(data_list)):
                prev = ''
                try:
                    client_emails = [data_list[i]['clientInfo'][j]['email']
                                        for j in range(len(data_list[i]['clientInfo']))]
                    setting_emails = [json.loads(data_list[i]['settings'])['clients'][j]['email'] for j in range(
                        len(json.loads(data_list[i]['settings'])['clients']))]

                    try:
                        k = 0
                        for j in range(len(client_emails)):
                            if client_emails[j] not in setting_emails:
                                del data_list[i]['clientInfo'][j-k]
                                k += 1
                    except Exception as e:
                        print("hi2" +e)

                    inbound = data_list[i]['clientInfo']
                    setting = json.loads(data_list[i]['settings'])[
                        'clients']
                    sorted_inbound = sorted(inbound, key=lambda x: [
                        d['email'] for d in setting].index(x['email']))
                    data_list[i]['clientInfo'] = sorted_inbound

                    for j in range(len(data_list[i]['clientInfo'])):

                        if prev == json.loads(data_list[i]['settings'])['clients'][j]:
                            break
                        prev = json.loads(data_list[i]['settings'])[
                            'clients'][j]

                        data_list[i]['clientInfo'][j]['settings'] = str(
                            json.loads(data_list[i]['settings'])['clients'][j])
                        new_list.append(data_list[i]['clientInfo'][j])

                except Exception as e:
                    print(e)

            data_list = new_list
        
        else:
            for i in range(len(data_list)):
                data_list[i]['email'] = data_list[i].pop('remark')
                data_list[i].pop('streamSettings')
                data_list[i].pop('sniffing')
                data_list[i].pop('tag')

        lists.extend(data_list)
        print(f"{panel_name} : geting data successful")
    
    open(json_file, 'w').close()
    write_json(lists)


if __name__ == '__main__':
    save_accounts_to_json()
