#!/bin/bash

filetime=$(date +"%Y_%m_%d_%H:%M:%S")

pg_dump -U mlflow -d mlruns > /tmp/backups/backup_$filetime.sql