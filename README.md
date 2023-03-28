## V2Ray Telegram bot: **Getting V2Ray account information through a Telegram bot.**

## How to install
1. Install Git, Python 3, and Pip 3 on your system. Run `apt install git python3 python3-pip` to install dependencies.
2. Clone the project with `git clone https://github.com/TeleDark/v2ray-tel-bot.git && cd v2ray-tel-bot`.
3. Install required packages using `pip install -r requirements.txt`.
4. Edit `login.py` and provide panel information to server values. Edit with `vim login.py`.
5. Automate the login process and retrieve data from the panels by running the `crontab -e` command. To update data every 5 minutes, add the following text to the last line: `*/5 * * * * python3 /root/v2ray-tel-bot/login.py`.
6. Edit keys.py to set your bot token.
7. Run the Telegram bot using `nohup python3 bot.py`.
8. If you want the bot to run again after the server is restarted, run the `crontab -e` command and add the following text to the last line: `@reboot python3 /root/v2ray-tel-bot/bot.py`.
