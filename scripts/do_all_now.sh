#!/bin/bash
# Automated setup script

# Update package lists
sudo apt-get update

# Install necessary packages
sudo apt-get install -y git nodejs npm

# Clone the repository
git clone https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI.git

# Navigate into the directory
cd Top-TieR-Global-HUB-AI

# Install project dependencies
npm install

# Run the project
npm start