#!/bin/bash

# Check if docker is installed

function set_up_enviroment_variable() {
    env_name=$1
    text=$2
    store_config=$3
    is_secrect=$4
    file=$5

    env_value=$(grep -E "^$env_name" $file | cut -d '=' -f2)
    if [ -z "$env_value" ]; then
        read -p "Enter the $text: " env_value
    else
        if [[ $is_secrect = false ]]; then
            echo "$env_name=$env_value"
        fi
        read -p "Do you want to change the $text? (leave empty for no change): " env_value
    fi

    if [ ! -z "$env_value" ] && ([ $store_config = 'y' ] || [ $store_config = 'Y' ]); then
        grep -q "^$env_name" $file && sed -i "/^$env_name/c\\$env_name=$env_value" $file || echo "$env_name=$env_value" >>$file
    fi
}

function set_up_backup(){
    store_config=$1

    backup_freq_is_correct=false
    while [ "$backup_freq_is_correct" = false ]; do
        echo -e "What backup frequency do you want (database)?\n\t0. None\n\t1. 30 minutes\n\t2. 1 hour\n\t3. 12 hours\n\t4 Daily\n\t5. Weekly\n\t6. Monthly" 
        read -p "[0-6]: " option_back
        case "$option_back" in
            0)
                backup_freq_is_correct=true
                ;;
            1)
                backup_freq_is_correct=true
                backup_freq="*/30 * * * *"
                ;;
            2)
                backup_freq_is_correct=true
                backup_freq="0 * * * *"
                ;;
            3) 
                backup_freq_is_correct=true
                backup_freq="0 */12 * * *"
                ;;
            4) 
                backup_freq_is_correct=true
                backup_freq="0 0 * * *"
                ;;
            5)
                backup_freq_is_correct=true
                backup_freq="0 0 * * 0"
                ;;
            6) 
                backup_freq_is_correct=true
                backup_freq="0 0 1 * *"
                ;;
            *)
                echo "Invalid option, it has to be between 0 and 6, obtain: $option_back"
        esac

        if [[ $backup_freq_is_correct = true ]] && [[ $option_back -ne 0 ]]; then
            crontab -l 2>/dev/null | grep -v "$(pwd)/backup_database.sh" | crontab -
            backup_command="$backup_freq $(pwd)/backup_database.sh $(pwd) >> $(pwd)/logs/backups.log 2>&1" 
            (crontab -l 2>/dev/null; echo "$backup_command") | crontab -
        fi
    done

    read -p "Do you want to remove the backups? [Y/n]" removal_opt_entrie
    if [[ $option_back -ne 0 ]] && ([[ $removal_opt_entrie = 'y' ]] || [[ $removal_opt_entrie = 'Y' ]] || [[ -z $removal_opt_entrie ]]); then
        is_removal_option_correct=false
        while [[ "$is_removal_option_correct" = false ]]; do
            case "$option_back" in
                1|2|3|4)
                    echo -e "Removal of backups: \n\t1. Dayly\n\t2. Weekly\n\t3. Monthly"
                    read -p "[1-3]: " removal_opt
                    ;;
                5|6)
                    echo -e "Removal of backups: \n\t1. Weekly\n\t2. Monthly" 
                    read -p "[1-2]: " removal_opt
                    removal_opt=$(($removal_opt + 1))
                    ;;
                7)
                    removal_opt=3
                    ;;
            esac
            if [[ $removal_opt -ge 1 ]] && [[ $is_removal_option_correct -le 3 ]]; then
                is_removal_option_correct=true
            fi
        done
    else
        removal_opt=0
    fi

    if [[ $store_config ]]; then
        grep -q "^BACK_UP_REMOVAL" .env && \
            sed -i "/^BACK_UP_REMOVAL/c\\BACK_UP_REMOVAL=$removal_opt" .env || \
            echo "BACK_UP_REMOVAL=$removal_opt" >>.env
    fi
}

echo "Starting installation process..."
if ! command -v docker &> /dev/null; then
    echo "Docker installation not found. Please install docker."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "Docker-compose installation not found. Please install docker-compose."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    touch .env
fi

# Backups
mkdir -p backups
chmod g+s backups

# Logs
mkdir -p logs
chmod g+s logs
touch logs/backups.log
chmod 0777 logs/backups.log

read -p "Do you want to make changes in the .env file? (y/N): " change_env

if [[ ! -z $change_env ]] && ([[ $change_env = 'y' ]] || [[ $change_env = 'Y' ]]); then
    read -p "Do you want to store the configuration in .env file? (y/N): " store_config
    set_up_enviroment_variable "MLFLOW_VERSION" "mlflow version" $store_config false .env
    set_up_enviroment_variable "MLFLOW_DOMAIN" "mlflow domain" $store_config false .env
    set_up_enviroment_variable "STATUS_DOMAIN" "status doamin" $store_config false .env
    set_up_enviroment_variable "POSTGRES_PASSWORD" "postgres password" $store_config true .env
    set_up_enviroment_variable "DEFAULT_ARTIFACT_ROOT" "artifact location" $store_config false .env
    set_up_enviroment_variable "START_PORT" "start port" $store_config false .env
    set_up_enviroment_variable "END_PORT" "end port" $store_config false .env

    read -p 'Are you using S3/AWS [S](default) or HDFS/GCP [H]? ' type_of_server
    if [[ -z $type_of_server ]] || [[ $type_of_server = 'S' ]] || [[ $type_of_server = 's' ]]; then
    	set_up_enviroment_variable "AWS_REGION" "AWS region" $store_config false .env 
        set_up_enviroment_variable "AWS_ACCESS_KEY_ID" "AWS access key id" $store_config true .env
        set_up_enviroment_variable "AWS_SECRET_ACCESS_KEY" "AWS secret access key" $store_config true .env
    fi

    set_up_backup $store_config

    set_up_enviroment_variable "TELEGRAM_TOKEN" "Telegram token" $store_config true .env
    set_up_enviroment_variable "TELEGRAM_TOKEN_NOTIFICATIONS" "Telegram token notifications" $store_config true .env 
    set_up_enviroment_variable "TELEGRAM_BACKUP_NOTIFICATIONS_ID" "Telegram bot id for backup_notifications" $store_config false .env 

    set_up_enviroment_variable "EMAIL_SENDER_ADDRESS" "Email sender address" $store_config false .env
    set_up_enviroment_variable "EMAIL_SENDER_TOKEN" "Email sender token" $store_config true .env

    set_up_enviroment_variable "MONGODB_USER" "MongoDB user" $store_config true .env
    set_up_enviroment_variable "MONGODB_PASSWORD" "MongoDB password" $store_config true .env
fi

read -p "If this is the first time you are running this script you would need to create a user in Uptime Kuma, do you want to just launch Uptime Kuma? (y/N): " launch_uptime_kuma
if [[ ! -z $launch_uptime_kuma ]] && ([[ $launch_uptime_kuma = 'y' ]] || [[ $launch_uptime_kuma = 'Y' ]]); then
    docker compose up -d
    uptime_kuma_url=$(grep -E "^STATUS_DOMAIN" .env | cut -d '=' -f2)
    echo "Uptime Kuma is running in http://$uptime_kuma_url, please create a user and then press enter to continue" 
    read -p "Press enter to continue"

    set_up_enviroment_variable "UPTIME_KUMA_USER" "Uptime kuma user" true false .env
    set_up_enviroment_variable "UPTIME_KUMA_PASSWORD" "Uptime kuma password" true true .env

    python3 -m venv venv
    . venv/bin/activate
    python -m pip install --upgrade pip
    pip install uptime_kuma_api dotenv
    deactivate

    rm -rf venv
    docker compose down
fi

read -p "Do you want to start the containers? (y/N): " start_containers
if [[ ! -z $start_containers ]] && ([[ $start_containers = 'y' ]] || [[ $start_containers = 'Y' ]]); then
    read -p "Do you want to build the containers? (y/N): " build_containers
    if [[ ! -z $build_containers ]] && ([[ $build_containers = 'y' ]] || [[ $build_containers = 'Y' ]]); then
        docker compose up -d --build
    else
        docker compose up -d
    fi
fi
