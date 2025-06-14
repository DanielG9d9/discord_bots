if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Please use sudo."
    exit 1
fi

echo "########################################################################"
echo "You will need to enter the token in the .env for the bot to run."
read -p "Have you set the DISCORD_TOKEN in the .env file? (y/n): " answer

answer=$(echo "$answer" | xargs)  # Trim whitespace
if [[ ! "$answer" =~ ^[Yy]$ ]]; then
    echo "Please set the DISCORD_TOKEN in the .env file before proceeding."
    echo "You can find the .env file in the project directory."
    echo "Exiting the script."
    exit 1
fi

echo "########################################################################"
echo "Preparing system to run the bot..."
echo "########################################################################"
sudo systemctl daemon-reload
sudo systemctl enable discordbot.service
sudo systemctl start discordbot.service
echo "########################################################################"
echo "Discord bot service started and enabled to run on boot."
echo "Checking the status of the Discord bot service..."
echo "########################################################################"
sudo systemctl status discordbot.service


echo "If you see 'Active: active (running)', the bot is running successfully."
echo "If you see 'Active: inactive (dead)' or 'failed', check the logs for errors."