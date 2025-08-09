import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
import threading
import requests
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_BOT")
api_url = "https://website-rt6b.onrender.com"
log_channel_id = 1393717563304710247

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_userid(ch):
    return ch.name

@bot.event
async def on_ready():
    await bot.tree.sync()

@bot.tree.command(name="resetdb", description="Wipes user data for this channel")
async def resetdb(interaction: discord.Interaction):
    uid = get_userid(interaction.channel)
    try:
        requests.post(f"{api_url}/disconnect", json={"userid": uid})
        await interaction.response.send_message(f"Data wiped for `{uid}`.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="deletechan", description="Delete this user's channel")
async def deletechan(interaction: discord.Interaction):
    uid = get_userid(interaction.channel)
    try:
        requests.post(f"{api_url}/disconnect", json={"userid": uid})
        await interaction.response.send_message("Deleting channel...")
        await interaction.channel.send("offline (deleting ts)")
        await asyncio.sleep(2)
        await interaction.channel.delete()
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="log", description="Send a log message")
@app_commands.describe(message="Message to log")
async def log(interaction: discord.Interaction, message: str):
    try:
        await bot.get_channel(log_channel_id).send(f"[LOG] {message}")
        await interaction.response.send_message("Logged!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="kick", description="Kick the user with a reason")
@app_commands.describe(reason="Reason for kicking")
async def kick(interaction: discord.Interaction, reason: str):
    uid = get_userid(interaction.channel)
    cmd = f'kick("{reason}")'
    try:
        requests.post(f"{api_url}/send_command/{uid}", json={"command": cmd})
        await interaction.response.send_message(f"Sent kick to `{uid}` for `{reason}`.")
        await interaction.channel.send(f"User `{uid}` was kicked for: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="say", description="Make the user say something")
@app_commands.describe(message="Message to send")
async def say(interaction: discord.Interaction, message: str):
    uid = get_userid(interaction.channel)
    cmd = f'chat("{message}")'
    try:
        requests.post(f"{api_url}/send_command/{uid}", json={"command": cmd})
        await interaction.response.send_message(f"Sent message to `{uid}`: `{message}`")
        await interaction.channel.send(f"`{uid}` said: {message}")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="help", description="List commands")
async def help_cmd(interaction: discord.Interaction):
    text = (
        "@everyone **Commands:**\n"
        "/resetdb\n"
        "/deletechan\n"
        "/log [message]\n"
        "/kick [reason]\n"
        "/say [message]\n"
        "/help"
    )
    await interaction.response.send_message("Help posted in channel.")
    await interaction.channel.send(text)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

bot.run(token)
