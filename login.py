import requests
import json


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


json_file = "accounts_info.json"

# write data in json file
def write_json(json_data):
    with open(json_file, 'a') as f:
        json.dump(json_data, f)


# login to all panels and save data
def login():
    with open(json_file, 'w') as f:
        lists = []
    status = True
    for server in servers:
        payload = {
            "username": server['user_panel'],
            "password": server['pass_panel']
        }

        session = requests.Session()
        response = session.post(server['url'] + url_login, data=payload)

        if 'false' in response.text:
            print(f"login Failed server {server['url']}")
            status = False

        if status:
            list = session.post(server['url'] + url_lists).json()['obj']
            lists.extend(list)

    write_json(lists)


if __name__ == '__main__':
    login()
