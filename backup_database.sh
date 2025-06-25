#!/bin/bash

cd $1

docker exec postgres /root/make_backup.sh

if [[ $? -eq 0 ]]; then
    msg="Backup was succesful at $(date +"%Y_%m_%d_%H:%M:%S")"

    backup_removal_opt=$(grep -E "^BACK_UP_REMOVAL" .env | cut -d '=' -f2)

    case "$backup_removal_opt" in
        1)
            removed_files=$(find backups -type f -mtime +0)
            echo "Backups of yesterday have been removed:"
            ;;
        2)
            removed_files=$(find backups -type f -mtime +7)
            echo "Backups of last week have been removed:"
            ;;
        3)
            removed_files=$(find backups -type f -mtime +31)
            echo "Backups of last month have been removed:"
            ;;
    esac

    rm -f $removed_files
    msg="$msg Removed backups: $removed_files"
    echo $msg
else
    msg="Backup unsuccesful at $(date +"%Y_%m_%d_%H:%M:%S")"
    echo $msg  
fi

cd remote_logs
. remote_logs/bin/activate
echo $msg
python send_logs.py "backup" $msg
deactivate

