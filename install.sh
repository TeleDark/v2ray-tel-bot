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
    # Install prerequisites for Python virtual environment
    apt-get install -y python3-full python3-venv python3-pip

    # Clone or update repository first
    if [ -d "$wk_dir/$config_dir" ]; then
        echo -e "${green}Backing up existing config...${plain}"
        cp -r $wk_dir/$config_dir ~/
        rm -rf $wk_dir
        cd ~/ && git clone $git_url &&
        cp -r ~/$config_dir $wk_dir/ && rm -rf ~/$config_dir
    else
        echo -e "${green}Cloning repository...${plain}"
        rm -rf $wk_dir
        cd ~/ && git clone $git_url;
    fi

    # Create virtual environment AFTER cloning repository
    echo -e "${green}Creating Python virtual environment...${plain}"
    python3 -m venv "$wk_dir/venv"

    # Activate virtual environment
    echo -e "${green}Activating virtual environment...${plain}"
    source "$wk_dir/venv/bin/activate"

    # Upgrade pip and setuptools within virtual environment
    echo -e "${green}Upgrading pip and setuptools...${plain}"
    "$wk_dir/venv/bin/pip" install --upgrade pip setuptools || { 
        echo -e "${red}Failed to upgrade pip/setuptools${plain}"; exit 1; 
    }

    # Install Python dependencies using virtual environment pip
    echo -e "${green}Installing Python dependencies...${plain}"
    "$wk_dir/venv/bin/pip" install PyYAML || { 
        echo -e "${red}Failed to install PyYAML${plain}"; exit 1; 
    }
    
    "$wk_dir/venv/bin/pip" install -r "$wk_dir/requirements.txt" || { 
        echo -e "${red}Failed to install all requirements together. Trying individual installations...${plain}";
        
        # Install packages individually if batch installation fails
        requirements=$(cat "$wk_dir/requirements.txt")
        for package in $requirements; do
            echo -e "${green}Installing $package...${plain}"
            "$wk_dir/venv/bin/pip" install "$package" || echo -e "${red}Failed to install $package, continuing...${plain}"
        done
    }

    # Set up cron jobs using virtual environment Python interpreter
    echo -e "${green}Setting up cron jobs...${plain}"
    (crontab -l 2>/dev/null; 
     echo "*/3 * * * * $wk_dir/venv/bin/python $wk_dir/login.py"; 
     echo "@reboot $wk_dir/venv/bin/python $wk_dir/bot.py"; 
     echo "42 2 */2 * * rm -rf $wk_dir/cookies.pkl") | sort -u | crontab - || { 
        echo -e "${red}Failed to set up cron jobs${plain}"; exit 1; 
    }

    echo -e "\n${green}Installation completed successfully!${plain}"
    echo -e "${green}Edit 'config.yml' in $wk_dir/$config_dir, then run 'reboot'.${plain}"
    echo -e "${green}The bot will start automatically after reboot.${plain}"
}

# Main execution
if [ -d "$wk_dir/$config_dir" ]; then
    echo -e "${green}Upgrading script...${plain}"
else
    echo -e "${green}Installing script...${plain}"
fi

install_base
check_python
