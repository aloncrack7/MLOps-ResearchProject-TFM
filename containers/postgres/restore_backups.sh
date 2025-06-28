#!/bin/bash

# Restore the latest backup from the backups directory

# Get the latest backup file
latest_backup=$(ls -t /tmp/backups/ | head -n 1)

# Restore the backup
pg_restore -U mflow -d mlruns -h localhost -p 5432 backups/$latest_backup