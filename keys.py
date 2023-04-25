import os
import yaml
real_dir = os.path.dirname(os.path.realpath(__file__))
json_file = os.path.join(real_dir,"accounts_info.json")
pickle_file = os.path.join(real_dir, "cookies.pkl")
config_yaml_file = os.path.join(real_dir, "config/config.yml")
msg_yaml_file = os.path.join(real_dir, "config/messages.yml")


# load yaml config
with open(config_yaml_file, 'r') as f:
    config_yaml = yaml.safe_load(f)

# load yaml messages
with open(msg_yaml_file, 'r') as f:
    msg_yaml = yaml.safe_load(f)

telegram_token = config_yaml["telegram_token"]
panels = config_yaml["panels"]