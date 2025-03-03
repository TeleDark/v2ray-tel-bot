#!/bin/bash
red='\033[0;31m'
green='\033[0;32m'
plain='\033[0m'
wk_dir=~/v2ray-tel-bot
config_dir=config
config_file=config.yml
git_url="https://github.com/TeleDark/v2ray-tel-bot.git"

# Check root
[[ $EUID -ne 0 ]] && echo -e "${red}Fatal error: Please run this script with root privilege${plain}" && exit 1

# Check OS
if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    release=$ID
elif [[ -f /usr/lib/os-release ]]; then
    source /usr/lib/os-release
    release=$ID
else
    echo -e "${red}Failed to identify OS. Please contact the author!${plain}" >&2
    exit 1
fi

install_base() {
    case "${release}" in
        centos|fedora)
            echo -e "${red}CentOS/Fedora not supported yet. Use an Ubuntu/Debian-based system.${plain}"
            exit 1
            ;;
        ubuntu|debian)
            apt-get update -y || { echo -e "${red}Failed to update package list${plain}"; exit 1; }
            apt-get install -y git wget python3 cron libzbar0 zbar-tools || { echo -e "${red}Failed to install base packages${plain}"; exit 1; }
            ;;
        *)
            echo -e "${red}Unsupported OS: $release. This script requires Ubuntu or Debian.${plain}"
            exit 1
            ;;
    esac
}

check_python() {
    # Check if python3 exists and get version
    if command -v python3 >/dev/null 2>&1; then
        python_ver=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
        echo -e "${green}Detected Python version: $python_ver${plain}"
        if python3 -c "import sys; print(sys.version_info[:2] >= (3, 10))" | grep -q "True"; then
            echo -e "${green}Python >= 3.10 already installed${plain}"
        else
            echo -e "${green}Installing Python 3.10${plain}"
            apt-get install -y software-properties-common || { echo -e "${red}Failed to install software-properties-common${plain}"; exit 1; }
            add-apt-repository -y ppa:deadsnakes/ppa || { echo -e "${red}Failed to add PPA${plain}"; exit 1; }
            apt-get update -y || { echo -e "${red}Failed to update after adding PPA${plain}"; exit 1; }
            apt-get install -y python3.10 python3.10-distutils || { echo -e "${red}Failed to install Python 3.10${plain}"; exit 1; }
            update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
        fi
    else
        echo -e "${green}No Python 3 detected. Installing Python 3.10${plain}"
        apt-get install -y software-properties-common || { echo -e "${red}Failed to install software-properties-common${plain}"; exit 1; }
        add-apt-repository -y ppa:deadsnakes/ppa || { echo -e "${red}Failed to add PPA${plain}"; exit 1; }
        apt-get update -y || { echo -e "${red}Failed to update after adding PPA${plain}"; exit 1; }
        apt-get install -y python3.10 python3.10-distutils || { echo -e "${red}Failed to install Python 3.10${plain}"; exit 1; }
        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    fi

    # Install pip explicitly using get-pip.py
    if ! command -v pip3 >/dev/null 2>&1 || ! pip3 --version | grep -q "python 3.10"; then
        echo -e "${green}Installing fresh pip for Python 3.10${plain}"
        curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py || { echo -e "${red}Failed to download get-pip.py${plain}"; exit 1; }
        python3 get-pip.py --force-reinstall || { echo -e "${red}Failed to install pip${plain}"; exit 1; }
        rm -f get-pip.py
    else
        echo -e "${green}Pip already installed: $(pip3 --version)${plain}"
    fi

    # Ensure pip is usable and upgrade it
    /usr/local/bin/pip3 install --upgrade pip setuptools || { echo -e "${red}Failed to upgrade pip/setuptools${plain}"; exit 1; }

    # Clone or update repo
    if [ -d "$wk_dir/$config_dir" ]; then
        cp -r $wk_dir/$config_dir/$config_file ~/
        rm -rf $wk_dir
        cd ~/ && git clone $git_url &&
        cp -r ~/$config_file $wk_dir/$config_dir && rm -rf ~/$config_file
    else
        rm -rf $wk_dir
        cd ~/ && git clone $git_url;
    fi

    # Install dependencies using the updated pip
    /usr/local/bin/pip3 install --ignore-installed PyYAML || { echo -e "${red}Failed to install PyYAML${plain}"; exit 1; }
    /usr/local/bin/pip3 install --ignore-installed -r "$wk_dir/requirements.txt" || { 
        echo -e "${red}Failed to install all requirements together. Trying individual installations...${plain}";

        requirements=$(cat "$wk_dir/requirements.txt")
        for package in $requirements; do
            echo -e "${green}Installing $package...${plain}"
            /usr/local/bin/pip3 install --ignore-installed "$package" || echo -e "${red}Failed to install $package, continuing...${plain}"
        done
    }

    # Set up cron jobs
    (crontab -l 2>/dev/null; echo "*/3 * * * * python3 ~/v2ray-tel-bot/login.py"; echo "@reboot python3 ~/v2ray-tel-bot/bot.py"; echo "42 2 */2 * * rm -rf ~/v2ray-tel-bot/cookies.pkl") | sort -u | crontab - || { echo -e "${red}Failed to set up cron jobs${plain}"; exit 1; }

    echo -e "\n${green}Edit 'config.yml' in $wk_dir/$config_dir, then run 'reboot'. The bot will start after reboot.${plain}"
}

# Main execution
if [ -d "$wk_dir/$config_dir" ]; then
    echo -e "${green}Upgrading script...${plain}"
else
    echo -e "${green}Installing script...${plain}"
fi

install_base
check_python