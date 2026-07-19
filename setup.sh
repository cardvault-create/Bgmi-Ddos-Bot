#!/bin/bash
# Auto setup for each VPS

NODE_NUM=$1

echo "[+] Setting up Node $NODE_NUM..."

# Update system
sudo apt update -y
sudo apt upgrade -y

# Install Python
sudo apt install python3-pip screen -y

# Install libraries
pip3 install telethon colorama

# Create folder
mkdir -p ~/node

# Download files (ya copy karo)
cd ~/node

# Run node
screen -dmS attack python3 node.py $NODE_NUM

echo "[✓] Node $NODE_NUM Running!"
echo "Check: screen -r attack"
