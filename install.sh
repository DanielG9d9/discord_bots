#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Please use sudo."
    exit 1
fi

echo "########################################################################"
echo "Preparing system for install..."
echo "########################################################################"

# Save the opening directory as the project_file_path
project_dir=$(pwd)
repo_file_name="discord_bots"
program_name="main.py"
bot_venv="discordBotEnv/bin/activate"
user_name=$(whoami)
sudo apt-get update # Update package lists
sudo apt-get install -y git python3-venv feh # Install dependencies

cd /home/$USER/Desktop/discord_bots
cat << EOF > .env # Create .env file for environment variables
DISCORD_TOKEN=your_discord_token_here

EOF

echo "########################################################################"
echo "Creating virtual environment..."
python3 -m venv discordBotEnv # Create a virtual environment named discordBotEnv
echo "Virtual environment created at $project_dir/$bot_venv"
echo "Activating environment"
source $bot_venv # Activate the virtual environment
echo "########################################################################"
echo "Installing dependencies..."
# Install Python dependencies
pip install -r requirements.txt
echo "Requirements installed... Exiting venv."
deactivate # Deactivate the virtual environment
echo "########################################################################"

# Activate the virtual environment
source $project_dir/$bot_venv # This should point to the virtual environment of the repository.

cat << EOF > "/etc/systemd/system/discordbot.service" # Create service file for systemd

[Unit]
Description=Discord.py Bot Service
After=network.target

[Service]
Type=simple
User=$user_name
WorkingDirectory=$project_dir
ExecStart=$project_dir/discordBotEnv/bin/python $program_name
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

EOF

echo "Installation complete!"
echo "########################################################################"