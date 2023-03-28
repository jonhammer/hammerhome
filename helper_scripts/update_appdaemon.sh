#!/bin/bash

# Define the SSH connection parameters
REMOTE_USER="pi"
REMOTE_HOST="controller.local"

# SSH into the remote server and execute the commands
ssh ${REMOTE_USER}@${REMOTE_HOST} << EOF
    echo "Logging into remote server..."
    cd /home/pi/hammerhome/app_daemon
    echo "Changing directory..."
    git pull
    echo "Performing git pull..."
    sudo docker compose down
    echo "Stopping Docker containers..."
    sudo docker compose up -d
    echo "Starting Docker containers..."
EOF

