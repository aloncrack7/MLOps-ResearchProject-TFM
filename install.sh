#!/bin/bash

# Check if docker is installed

function set_up_enviroment_variable() {
    env_name=$1
    text=$2
    store_config=$3

    env_value=$(grep -E "^$env_name" .env | cut -d '=' -f2)
    if [ -z "$env_value" ]; then
        read -p "Enter the $text: " env_value
    else
        echo "$env_name=$env_value"
        read -p "Do you want to change the $text? (leave empty for no change): " env_value
    fi

    if [ ! -z "$env_value" ] && ([ $store_config = 'y' ] || [ $store_config = 'Y' ]); then
        grep -q "^$env_name" .env && sed -i "/^$env_name/c\\$env_name=$env_value" .env || echo "$env_name=$env_value" >>.env
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

read -p "Do you want to make changes in the .env file? (y/N): " change_env

if [ ! -z $change_env ] && ([ $store_config = 'y' ] || [ $store_config = 'Y' ]); then
    read -p "Do you want to store the configuration in .env file? (y/N): " store_config
    set_up_enviroment_variable "MLFLOW_DOMAIN" "mlflow domain" $store_config
    set_up_enviroment_variable "STATUS_DOMAIN" "status doamin" $store_config
fi

. .env

docker compose up -d
