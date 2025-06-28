#!/bin/bash

# Call the restore_backups.sh script in the postgres container
docker exec -it postgres /root/restore_backups.sh