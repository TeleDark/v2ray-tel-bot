import re
import requests
import json
from keys import *

url_login = "login"
url_lists = "xui/inbound/list"

# get panel authentication info
servers = [

    {
        'url': "panel url example: https://iran.example.com:7000/",
        'user_panel': 'admin',
        'pass_panel': 'admin',
    },
    # {
    #     'url': "https://iran.example.com:7000/",
    #     'user_panel': 'admin',
    #     'pass_panel': 'admin'
    # },

]


# write data in json file
def write_json(json_data):
    with open(json_file, 'a') as f:
        json.dump(json_data, f)


# login to all panels and save data
def login():
    open(json_file, 'w').close()
    lists = []
    new_list = []

    for server in servers:
        server_name = re.findall(r"http.?://(.*):", server['url'])[0]
        payload = {
            "username": server['user_panel'],
            "password": server['pass_panel']
        }

        session = requests.Session()
        response = session.post(server['url'] + url_login, data=payload)

        if response.json()['success']:
            list = session.post(server['url'] + url_lists).json()['obj']
            try:
                for i in range(len(list)):
                    prev = ''
                    for j in range(len(list[i]['clientStats'])):
                        if prev == json.loads(list[i]['settings'])['clients'][0]['id']:
                            break
                        prev = json.loads(list[i]['settings'])[
                            'clients'][0]['id']

                        list[i]['clientStats'][j]['settings'] = str(
                            json.loads(list[i]['settings'])['clients'][j])
                        new_list.append(list[i]['clientStats'][j])
                list = new_list
            except KeyError:
                pass

            lists.extend(list)
            print(f"{server_name} ➜ login successful")
        else:
            print(f"{server_name} ➜ wrong user name or password")

    write_json(lists)


if __name__ == '__main__':
    login()
