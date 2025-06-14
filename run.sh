if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Please use sudo."
    exit 1
fi


echo "You will need to enter the token for the bot to run."
echo "Have you done that? (y/n)"
read -r answer
if [[ "$answer" != "y" ]]; then
    echo "Please set the DISCORD_TOKEN in the .env file before proceeding."
    exit 1
fi
echo "########################################################################"
echo "Preparing system to run the Discord bot..."
echo "########################################################################"
sudo systemctl daemon-reload
sudo systemctl enable discordbot.service
sudo systemctl start discordbot.service
echo "Discord bot service started and enabled to run on boot."
echo "########################################################################"
echo "Checking the status of the Discord bot service..."
echo "########################################################################"
sudo systemctl status discordbot.service


echo "If you see 'Active: active (running)', the bot is running successfully."
echo "If you see 'Active: inactive (dead)' or 'failed', check the logs for errors."