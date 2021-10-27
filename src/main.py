import asyncio
import sys

from pymongo import MongoClient

import cogs._json

# Standard libraries
import os
import json
import logging
import datetime

# Third party libraries
import discord
from pathlib import Path
import motor.motor_asyncio
from discord.ext import commands

# Local code
import utils.json_loader
from utils.mongo import Document

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"(cwd)\n-----")

async def get_prefix(bot, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or("-")(bot, message)

    try:
        data = await bot.config.find(message.guild.id)

        # Make sure there is a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or("-")(bot,message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or('-')(bot, message)

secret_file = json.load(open(cwd+'\\secrets.json'))
intents = discord.Intents.default()
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix=get_prefix,case_insensitive=True,intents=intents)
bot.config_token = secret_file['token']
bot.connection_url = secret_file["mongo"]
logging.basicConfig(level=logging.INFO)

bot.blacklisted_users = []
bot.cwd = cwd

bot.version = '0.0.10'

confirmEmojis=[
'🇾',
'🇳'
]
bot.colors = {
    'WHITE': 0xFFFFFF,
    'AQUA': 0x1ABC9C,
    'GREEN': 0x2ECC71,
    'BLUE': 0x3498DB,
    'PURPLE': 0x9B59B6,
    'LUMINOUS_VIVID_PINK': 0xE91E63,
    'GOLD': 0xF1C40F,
    'ORANGE': 0xE67E22,
    'RED': 0xE74C3C,
    'NAVY': 0x34495E,
    'DARK_AQUA': 0x11806A,
    'DARK_GREEN': 0x1F8B4C,
    'DARK_BLUE': 0x206694,
    'DARK_PURPLE': 0x71368A,
    'DARK_VIVID_PINK': 0xAD1457,
    'DARK_GOLD': 0xC27C0E,
    'DARK_ORANGE': 0xA84300,
    'DARK_RED': 0x992D22,
    'DARK_NAVY': 0x2C3E50
}
bot.color_list = [c for c in bot.colors.values()]

cluster = MongoClient(bot.connection_url)

db = cluster["HomieBot"]
items = db["items"]
config = db["config"]
collection = db["HighScore"]
userData = db["userData"]

@bot.event
async def on_ready():
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\nMy current prefix is: -\n-----\nDiscord version: "+discord.__version__+"\n-----")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f" your complaints sucks. Hi, my name's {bot.user.name}.\nUse - to interact with me!"
                                                         f"\nI am snarky!"))
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["HomieBot"]
    bot.items = Document(bot.db, "items")
    bot.config = Document(bot.db, "config")
    bot.character = Document(bot.db, "character")
    print("Initialized Database\n-----")
    for document in await bot.config.get_all():
        print(document)
    for document in await bot.character.get_all():
        print(document)
"""
just can't get emoji confirmation menu to work
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    channel = payload.channel_id
    guild = payload.guild_id
    user = payload.user_id
    if user == bot.user.id:
        return

    reaction = str(payload.emoji)
    if reaction not in confirmEmojis:
        return

    if str(payload.emoji.name) == confirmEmojis[0]:
        await user.channel.send("Enter new character name")
        character = await bot.wait_for('message', check=lambda message: message.author == user.id)
        char = str(character)
        await bot.character.upsert({"_id":user.id,
                                    'name': char,
                                    'health': 100,
                                    'gold': 50})
        await user.channel.send(f"Character {char} created")

    else:
        return
"""
@bot.event
async def on_message(message):
    #ignore messages sent by the bot itself
    if message.author.bot:
        return
    #makes sure users aren't blacklisted
    if message.author.id in bot.blacklisted_users:
        return

    #Whenever the bot is tagged, respond with its prefix
    if message.content.startswith(f"<@!{bot.user.id}>") and \
        len(message.content) == len(f"<@!{bot.user.id}>"):
        data = await bot.config.get_by_id(message.guild.id)

        if not data or "prefix" not in data:
            prefix = "-"
        else:
            prefix = data["prefix"]
        await message.channel.send(f"My prefix here is `{prefix}`", delete_after=15)
        await message.add_reaction('<:sus:761772816072441866>')

    await bot.process_commands(message)

if __name__ == '__main__':
    # When running this file, if it is the 'main' file
    # I.E its not being imported from another python file run this
    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")
    bot.run(bot.config_token)