## V2Ray Telegram bot: **Getting V2Ray account information through a Telegram bot.**

## Install & Upgrade

```
bash <(curl -Ls https://raw.githubusercontent.com/TeleDark/v2ray-tel-bot/main/install.sh)
```

## setup
1. Enter the bot source folder using the command `cd ~/v2ray-tel-bot/`
2. open the config.yml file and put your Telegram bot token and information related to your panels in it. open with `nano config/config.yml`.
3. If you want to customize the Telegram bot messages, edit the `messages.yml` file using the `nano config/messages.yml` command
4. restart your server using the `reboot` command.
<hr>


## Install with Docker

1. Install Docker:

   ```sh
   bash <(curl -sSL https://get.docker.com)
   ```

2. Clone the Project Repository:

   ```sh
   git clone https://github.com/TeleDark/v2ray-tel-bot.git
   cd v2ray-tel-bot
   ```
3. open the config.yml file and put your Telegram bot token and information related to your panels in it

   ```sh
   nano config/config.yml
   ```
5. Start the Service

   ```sh
   docker compose up -d
   ```


## Features
- **Account Information Retrieval**: Retrieve account information using QRCode, UUID, Vless, Vmess, Shadowsocks, and remark.
- **Dockerized**: The project is Dockerized for easy deployment and scalability.
- **Channel Membership Requirement**: Optionally, you can enforce users to join a specific channel before accessing the account information. You can configure the channel_id in the `config.yml` file.

<hr>
<div align="center">

### ▶️ Watch how to setup on YouTube.
[<img src="https://user-images.githubusercontent.com/46258401/233775650-fa95d39b-3ca0-4344-a5a7-9f3f1ec4c7d1.png" align="center" width="90%">](https://www.youtube.com/watch?v=6buiaJFwiUU "how to setup")
</div>

<hr>

## ❤️ Donate

### BTC
Address: `bc1qtx3s7vntrj2aa82kmxx37scyyhv2hgch2ljrc0`

### TRON
Address: `TFvdz2LxQRr5bPM5zrawH7UdaqA6jj5J4L`

### USDT (TRC-20)
Address: `TJwCKAVnD54xLWzjjb5YecspVVKgbJBvuH`
