# Written by Daniel Gray

from discord.ext import commands
from dotenv import load_dotenv
import discord
import logging
import os
from discord import app_commands
import datetime


load_dotenv()

token = os.getenv('TESTING_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# User variables
TestServer_BTC_ID = 1383138425351180422 # Test Server ID, use for testing on own server (Bitcoin focused Server)
TestServer_GENERAL = 1383149398694952991 # Test Server General Channel ID

Active_Server = TestServer_BTC_ID # Set the active server ID TestServer_BTC_ID or NormalNeutralName_ID
Active_Channel = TestServer_GENERAL # Set the active channel ID TestServer_GENERAL or NormalNeutralName_GENERAL


# Event Handlers
@bot.event
async def on_ready():
    await bot.tree.sync() # This registers the slash commands with Discord
    channel_id = Active_Channel  # Replace with your channel ID
    channel = bot.get_channel(channel_id)
    # if channel:
    #     await channel.send("Testing bot is online and ready to serve!")
    #     gif_url = ""
    #     await channel.send(gif_url)
    # else:
    #     print(f"Channel with ID {channel_id} not found.")
    
    # Start the periodic inactive member pruning task
    # bot.loop.create_task(prune_inactive_members_periodically())
    print(f"Bot is armed.")

@bot.tree.command(
    name="punnish",
    description="Timeout another user for x minutes.",
    guild=discord.Object(id=Active_Server)
)
@app_commands.describe(
    member="The member to timeout",
    minutes="Timeout duration in minutes (1-60)"
)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int = 1):
    """
    Timeout another user for "x" minutes.
    Usage: /timeout member: @user minutes: 5
    """
    if member is None or member == interaction.user:
        await interaction.response.send_message("You must mention another user to use this command.", ephemeral=True)
        return
    if minutes < 1 or minutes > 60:
        await interaction.response.send_message("Timeout duration must be between 1 and 60 minutes.", ephemeral=True)
        return
    timeout_duration = datetime.timedelta(minutes=minutes)
    try:
        if interaction.user.guild_permissions.administrator or any(role.name.lower() == "second officer" for role in interaction.user.roles):
            await member.timeout(timeout_duration, reason=f"Timed out by admin for {minutes} minute(s).")
            await interaction.response.send_message(f"{member.mention} has been timed out for {minutes} minute(s) by {interaction.user.mention}.")
            return

        await interaction.user.timeout(timeout_duration, reason=f"Tried to timeout another user for {timeout_duration} minutes?!")
        await interaction.response.send_message(
            f"{interaction.user.mention} tried to timeout {member.mention} for {minutes} minute(s), but timed themselves out instead!\n"
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWo4cWc2dDlkNGxpeDBmdHczbzd3M2xuOHJuYzkwdGpjY2FhbWEzcCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/zNXvBiNNcrjDW/giphy.gif"
        )
    except Exception as e:
        await interaction.response.send_message(f"Failed to timeout yourself: {e}", ephemeral=True)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)