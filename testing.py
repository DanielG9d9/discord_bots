# Written by Daniel Gray
# Running on Render.com <https://dashboard.render.com/web/srv-d169nm8gjchc73e7rdgg/settings>

from discord.ext import commands
from dotenv import load_dotenv
import datetime
import discord
import logging
import asyncio
import json
import pytz
import os


load_dotenv()

# Date format for displaying timestamps
DATE_FORMAT = '%m-%d-%Y %H:%M %Z'

token = os.getenv('TESTING_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# User variables
trigger_words = ["₿", "₿itcoin", "b i t c o i n", "b1tco1n", "b1tc01n","bitcoin", " btc", "btc", "ethereum", 
                 " eth",'ltc', "dogecoin", "litecoin",]  # Add more as needed
banned_words = ["ethereum", " eth", "e t h", "e t h e r e u m", " ltc", "dogecoin", "litecoin", ]
user_trigger_counts = {} # Dictionary to track user trigger counts
USER_COUNTS_FILE = "user_trigger_counts.json"
all_time_trigger_counts = {}
ALL_TIME_USER_COUNTS_FILE = "all_time_user_trigger_counts.json"
NormalNeutralName_ID = 1259530733433655503 # NNNR bitcoin channel ID
TestServer_ID = 1383138425351180422 # Test Server ID, use for testing on own server (Bitcoin focused Server)
NormalNeutralName_GENERAL = 1259529235496964177 # NNNR Server General Channel ID
TestServer_GENERAL = 1383149398694952991 # Test Server General Channel ID

Active_Server = TestServer_ID # Set the active server ID TestServer_ID or NormalNeutralName_ID
Active_Channel = TestServer_GENERAL # Set the active channel ID TestServer_GENERAL or NormalNeutralName_GENERAL

#functions
def save_user_trigger_counts():
    with open(USER_COUNTS_FILE, "w") as f:
        json.dump(user_trigger_counts, f)

def save_all_time_trigger_counts():
    with open(ALL_TIME_USER_COUNTS_FILE, "w") as f:
        json.dump(all_time_trigger_counts, f)
def load_user_trigger_counts():
    global user_trigger_counts
    try:
        with open(USER_COUNTS_FILE, "r") as f:
            user_trigger_counts.update({int(k): v for k, v in json.load(f).items()})
    except FileNotFoundError:
        user_trigger_counts = {}

def load_all_time_trigger_counts():
    global all_time_trigger_counts
    try:
        with open(ALL_TIME_USER_COUNTS_FILE, "r") as f:
            all_time_trigger_counts.update({int(k): v for k, v in json.load(f).items()})
    except FileNotFoundError:
        all_time_trigger_counts = {}
# Event Handlers
@bot.event
async def on_ready():
    load_user_trigger_counts()
    load_all_time_trigger_counts()
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
    bot.loop.create_task(prune_inactive_members_periodically())
    print(f"We are all Satoshi.")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server, {member.name}! I'll be watching you.")

@bot.event
async def on_member_leave(member):
    channel_id = Active_Server  # Replace with your channel ID
    channel = bot.get_channel(channel_id)
    await channel.send(f"Suck it, {member.name}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send(f"Hello, {message.author.name}!")
    
    if any(word in message.content.lower() for word in trigger_words): # If any words are trigger words
        if message.channel.id != Active_Server: # Bitcoin focused Server

            user_id = message.author.id
            user_trigger_counts[user_id] = user_trigger_counts.get(user_id, 0) + 1   # Update local counts
            all_time_trigger_counts[user_id] = all_time_trigger_counts.get(user_id, 0) + 1   # Update all-time counts
            save_user_trigger_counts()
            save_all_time_trigger_counts()
            print(f"User {message.author} has used a trigger word {user_trigger_counts[user_id]} times. \n Context: {message.content}")
        
            if any(word in message.content.lower() for word in banned_words):
                if user_trigger_counts[user_id] >= 3:
                    # If the user has used a banned word 3 times, delete the message and timeout the user
                    await message.delete()
                    timeout = user_trigger_counts[user_id] * 2 # Timeout duration is double the number of times the user has used a banned word.
                    timeout_duration = datetime.timedelta(minutes=timeout) # Timeout time grows
                    await message.channel.send(f"{message.author.mention} - Thank you for your message. You will now be timed out for using a banned word outside of <#bitcoin-chat-immutable>. {message.author.mention} has been timed out for {timeout} minutes.")
                    try:
                        print("Attempting to timeout user:", message.author.name)
                        await message.author.timeout(timeout_duration, reason="Used banned word outside allowed channel.")
                        print("User timed out successfully:", message.author.name)
                        gif_url_banned = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWJ4eGk4NGE2NWhyZXd5cDN4eDEybzA5aTM1eWRmMzlwaWNlNjRwdiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/oCMd930DS9Jz0eSVxh/giphy.gif"
                        await message.channel.send(gif_url_banned)
                    except Exception as e:
                        if message.author.guild_permissions.administrator:
                            await message.channel.send(f"{message.author.mention} - You are an admin, but even admins should follow the rules! Don't abouse your power!")
                        else:
                            await message.channel.send(f"Failed to timeout user: {e}. Consider yourself lucky, {message.author.mention}.")
                else:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} - Strike {user_trigger_counts[user_id]}! No shitcoining allowed, nerd.")
            else:
                if user_trigger_counts[user_id] >= 3:
                    timeout = user_trigger_counts[user_id] * 2 # Timeout duration is double the number of times the user has used a banned word.
                    timeout_duration = datetime.timedelta(minutes=timeout) # Timeout time grows
                    await message.channel.send(f"{message.author.mention} - Thank you for your message. You will now be timed out for using a banned word outside of <#bitcoin-chat-immutable>. {message.author.mention} has been timed out for {timeout} minutes.")
                    try:
                        print("Attempting to timeout user:", message.author.name)
                        await message.author.timeout(timeout_duration, reason="Used banned word outside allowed channel.")
                        print("User timed out successfully:", message.author.name)
                        gif_url_banned = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWJ4eGk4NGE2NWhyZXd5cDN4eDEybzA5aTM1eWRmMzlwaWNlNjRwdiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/oCMd930DS9Jz0eSVxh/giphy.gif"
                        await message.channel.send(gif_url_banned)
                    except Exception as e:
                        if message.author.guild_permissions.administrator:
                            await message.channel.send(f"{message.author.mention} - You are an admin, but even admins should follow the rules! Don't abouse your power!")
                        else:
                            await message.channel.send(f"Failed to timeout user: {e}. Consider yourself lucky, {message.author.mention}.")
                        
                else:
                    await message.channel.send(f"{message.author.mention} - Strike {user_trigger_counts[user_id]}! Please refrain from bringing up Bitcoin outside of the designated <#bitcoin-chat-immutable> channel.")

    # Process commands after handling the message
    await bot.process_commands(message)

@bot.command(name="triggers")
async def triggers(ctx, member: discord.Member = None):
    """Check how many trigger words a user has committed."""
    if member is None:
        member = ctx.author
    count = user_trigger_counts.get(member.id, 0)
    await ctx.send(f"{member.display_name} has triggered {count} time(s).")

@bot.command(name="all_time_triggers")
async def all_time_triggers(ctx, member: discord.Member = None):
    """Check how many trigger words a user has committed in total."""
    if member is None:
        member = ctx.author
    count = all_time_trigger_counts.get(member.id, 0)
    await ctx.send(f"{member.display_name} has triggered {count} time(s) in total.")

@bot.command(name="reset_triggers")
async def reset_triggers(ctx, member: discord.Member = None):
    """Admin can reset user trigger count (local)."""
    if ctx.author.guild_permissions.administrator:
        if member is None:
            member = ctx.author
        user_trigger_counts[member.id] = 0
        save_user_trigger_counts()
        await ctx.send(f"{member.display_name}'s trigger count has been reset.")
    else:
        await ctx.send("You do not have permission to use this command...")
        gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3ZhMmtzd2g5Ymd6OGllbDhkdjBkYzl4d2M1dWFhMGV4cTdtaGt2eiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/L0coY9I1D2BnaKln9a/giphy.gif"
        await ctx.send(gif_url)

@bot.command(name="timeout_left")
async def timeout_left(ctx, member: discord.Member = None):
    """Check how much time is left on a user's timeout."""
    if member is None:
        member = ctx.author
    if hasattr(member, "timed_out_until") and member.timed_out_until:
        now = datetime.datetime.now(datetime.timezone.utc)
        if member.timed_out_until > now:
            remaining = member.timed_out_until - now
            minutes, seconds = divmod(int(remaining.total_seconds()), 60)
            await ctx.send(f"{member.display_name} is timed out for another {minutes} minute(s) and {seconds} second(s).")
        else:
            await ctx.send(f"{member.display_name} is not currently timed out.")
    else:
        await ctx.send(f"{member.display_name} is not currently timed out.")

@bot.command(name="timeout")
async def timeout(ctx, member: discord.Member = None, minutes: int = 1):
    """
    Timeout another user for "x" minutes.
    Usage: !timeout @user 5
    """
    if member is None or member == ctx.author:
        await ctx.send("You must mention another user to use this command.")
        return
    if minutes < 1 or minutes > 60:
        await ctx.send("Timeout duration must be between 1 and 60 minutes.")
        return
    timeout_duration = datetime.timedelta(minutes=minutes)
    try:
        if ctx.author.guild_permissions.administrator or any(role.name.lower() == "second officer" for role in ctx.author.roles):
            await member.timeout(timeout_duration, reason=f"Timed out by admin for {minutes} minute(s).")
            await ctx.send(f"{member.mention} has been timed out for {minutes} minute(s) by {ctx.author.mention}.")
            return
        
        await ctx.author.timeout(timeout_duration, reason=f"Tried to timeout another user for {timeout_duration} minutes?!")
        await ctx.send(f"{ctx.author.mention} tried to timeout {member.mention} for {minutes} minute(s), but timed themselves out instead!")
        gif_url_banned = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWo4cWc2dDlkNGxpeDBmdHczbzd3M2xuOHJuYzkwdGpjY2FhbWEzcCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/zNXvBiNNcrjDW/giphy.gif"
        await ctx.send(gif_url_banned)
    except Exception as e:
        await ctx.send(f"Failed to timeout yourself: {e}")

@bot.command(name="untimeout")
async def untimeout(ctx, member: discord.Member = None):
    """Admin or 'second officer' can remove a user's timeout."""
    if member is None:
        await ctx.send("You must mention a user to remove their timeout.")
        return
    try:
        if ctx.author.guild_permissions.administrator or any(role.name.lower() == "second officer" for role in ctx.author.roles):
            await member.timeout(None, reason="Timeout removed by admin or second officer.")
            # Calculate how much time was served of the timeout
            if hasattr(member, "timed_out_until") and member.timed_out_until:
                now = datetime.datetime.now(datetime.timezone.utc)
                total_timeout = member.timed_out_until - member.timed_out_until.replace(microsecond=0)
                served = max(datetime.timedelta(0), now - (member.timed_out_until - total_timeout))
                minutes_served, seconds_served = divmod(int(served.total_seconds()), 60)
                await ctx.send(f"The divine council favors {member.display_name} with their blessing. {member.mention}, your timeout has been cut short after serving {minutes_served} minute(s) and {seconds_served} second(s).")
                gif_url_banned = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3prcHJrY3ZuZnNqajBxZ29pZGtqdWU5ZzdoanI0bXZtZGU0NWJ3NiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/tXTqLBYNf0N7W/giphy.gif"
                await ctx.send(gif_url_banned)
            else:
                await ctx.send("User is not currently timed out.")
        else:
            await ctx.send("You do not have permission to use this command.")
    except Exception as e:
        await ctx.send(f"Failed to remove timeout: {e}")

@bot.command(name="trigger_words")
async def trigger_words_cmd(ctx):
    """List all trigger words."""
    await ctx.send("Trigger words: " + ", ".join(trigger_words))

async def prune_inactive_members_periodically():
    await bot.wait_until_ready()
    while not bot.is_closed():
        for guild in bot.guilds:
            cutoff_30 = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)
            kicked = []
            warned_7 = []
            warned_1 = []
            for member in guild.members:
                if member.bot or member.guild_permissions.administrator:
                    continue
                last_activity = None

                # Check last message
                found_message = False
                for channel in guild.text_channels:
                    async for message in channel.history(limit=None, after=cutoff_30):
                        if message.author == member:
                            last_activity = message.created_at
                            found_message = True
                            break
                    if found_message:
                        break

                # Check last reaction
                if not last_activity:
                    found_reaction = False
                    for channel in guild.text_channels:
                        async for message in channel.history(limit=None, after=cutoff_30):
                            for reaction in message.reactions:
                                users = [u async for u in reaction.users()]
                                if member in users:
                                    last_activity = message.created_at
                                    found_reaction = True
                                    break
                            if found_reaction:
                                break
                        if found_reaction:
                            break

                now = datetime.datetime.now(datetime.timezone.utc)
                if not last_activity:
                    # No activity at all, treat as never active
                    inactive_days = 31
                else:
                    inactive_days = (now - last_activity).days

                # Warn at 23 days (7 days left)
                if inactive_days == 23:
                    warned_7.append(member)
                # Warn at 29 days (1 day left)
                if inactive_days == 29:
                    warned_1.append(member)
                # Kick at 30+ days
                if inactive_days >= 30:
                    try:
                        await member.kick(reason="Inactive for 30 days (no messages or reactions)")
                        kicked.append(member.display_name)
                    except Exception as e:
                        logging.warning(f"Failed to kick {member.display_name}: {e}")

            # Send warnings
            for member in warned_7:
                try:
                    await member.send(f"Hi {member.mention}, you have been inactive for 23 days in **{guild.name}**. If you don't send a message or react to anything in the next 7 days, you will be kicked from the server.")
                except Exception:
                    pass
            for member in warned_1:
                try:
                    await member.send(f"Hi {member.mention}, you have been inactive for 29 days in **{guild.name}**. If you don't send a message or react to anything in the next 1 day, you will be kicked from the server.")
                except Exception:
                    pass

            # Announce kicked members
            if kicked:
                log_channel = guild.system_channel or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                if log_channel:
                    await log_channel.send(f"Kicked {len(kicked)} inactive members: {', '.join(kicked)}")

        await asyncio.sleep(24 * 60 * 60)  # Run once every 24 hours

@bot.tree.command(name="last_active", description="Find the last time a member was active in the current channel.")
async def last_active(interaction: discord.Interaction, member: discord.Member):
    channel = interaction.channel
    last_message = None

    async for message in channel.history(limit=1000):
        if message.author == member:
            last_message = message
            break

    if last_message:
        eastern = pytz.timezone('US/Eastern')
        # Convert UTC datetime to US/Eastern, accounting for DST
        timestamp = last_message.created_at.astimezone(eastern).strftime(DATE_FORMAT)
        await interaction.response.send_message(
            f"{member.display_name} was last active in this channel at {timestamp}."
        )
    else:
        await interaction.response.send_message(
            f"No recent activity found for {member.display_name} in this channel."
        )

bot.run(token, log_handler=handler, log_level=logging.DEBUG)