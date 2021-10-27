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
from discord.ext import tasks

# Local code
import utils.json_loader
from utils.mongo import Document
import asyncio

class Character(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="create",
        description="Register your character with the bot!",
        usage="Type command then type a character name with no prefix",
    )
    async def create(self, ctx):
        """
        Type <prefix>create then, type a character name when prompted without a prefix
        """
        try:
            player = await self.bot.character.find(ctx.author.id)
            name = player.get('name')
        except:
            player=[]
        if player is not None:
            await ctx.send("Create a new player? You will lose everything and start over if you had a previous save (Y/N)")
            choice = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if choice.content == 'Y':
                await ctx.send("Please select a name for your new character")
                name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                char = str(name.content)

                await self.bot.character.upsert(({"_id":ctx.author.id,
                                                  'name': char,
                                                  'current_health': 100,
                                                  'total_health': 100,
                                                  'damage': 5,
                                                  'armor': 5,
                                                  'gold': 50}))
                await ctx.send(f"{char} has been born into the world!")
            else:
                await ctx.send("Your character "+str(name)+" persists!")
        else:
            await ctx.send("Please choose your character's name")
            name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            char = str(name.content)

            await self.bot.character.upsert(({"_id":ctx.author.id,
                                              'name': char,
                                              'current_health': 100,
                                              'total_health': 100,
                                              'damage': 5,
                                              'armor': 5,
                                              'gold': 50}))
            await ctx.send(f"{char} has been born into the world!")

    @commands.command(
        name="profile",
        aliases=['p','pstats'],
        description="Show's your character's current stats",
        usage="Type command by itself",
    )
    async def profile(self, ctx):
        """
        Type <prefix>p to see your character stats
        """
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)

        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create")
            return
        else:
            player["_id"] = ctx.author.display_name
            embed = discord.Embed(title=f'{player["_id"]} Stats', description='\uFEFF', color=ctx.author.colour, timestamp=ctx.message.created_at)
            try:
                embed.set_image(url=player["picture"])
            except:
                player["picture"] = "https://cached.imagescaler.hbpl.co.uk/resize/scaleHeight/815/cached.offlinehbpl.hbpl.co.uk/news/SUC/MEMAYY-20200316081851159.jpg"
                embed.set_image(url=player["picture"])
            embed.add_field(name='Character Name:',value=player["name"], inline=True)
            try:
                embed.add_field(name=str(player['current_health'])+'/'+str(player['total_health']),value="Health")
            except:
                player["current_health"] = 100
                player["total_health"] = 100
                embed.add_field(name=str(player['current_health'])+'/'+str(player['total_health']),value="Health",inline=False)
            try:
                embed.add_field(name='Damage:',value=player['damage'],inline=False)
            except:
                player['damage'] = 5
                embed.add_field(name='Damage:',value=player['damage'],inline=False)
            try:
                embed.add_field(name='Armor:',value=player['armor'],inline=False)
            except:
                player['armor'] = 5
                embed.add_field(name='Armor:',value=player['armor'],inline=False)
            embed.add_field(name='Gold:',value=player['gold'])

            embed.set_footer(text=f"Still under development? | {self.bot.user.name}")
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            await ctx.send(embed=embed)

    @commands.command(
        name="setPic",
        aliases=['sp'],
        description="Sets the player's profile pic if they exist",
        usage="Type <prefix>sp FULL_IMAGE_URL works for gifs too. Right click image from source and copy image url for correct one",
    )
    async def setPic(self, ctx, *, url='url'):
        """
        Type <prefix>sp IMAGE_URL to set your character profile pic
        """
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)

        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create")
            return

        else:
            await self.bot.character.upsert({"_id": ctx.author.id, "picture": url})

    @commands.command(
        name="pp",
        aliases=['otherp','otherProfile','playerProfile'],
        description="Finds and displays another player's profile if they exist",
        usage="Type <prefix>pp MENTION/USER-NAME can use either a mention or case-sensitive spelling of their Discord name"
    )
    async def pp(self, ctx, user:discord.Member):
        """
        Type <prefix>pp username to see another player's profile
        """
        try:
            player = await self.bot.character.find_by_id(user.id)

        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create")
            return
        else:
            player["_id"] = ctx.author.display_name
            embed = discord.Embed(title=f'{player["_id"]} Stats', description='\uFEFF', color=ctx.author.colour, timestamp=ctx.message.created_at)
            try:
                embed.set_image(url=player["picture"])
            except:
                player["picture"] = "https://cached.imagescaler.hbpl.co.uk/resize/scaleHeight/815/cached.offlinehbpl.hbpl.co.uk/news/SUC/MEMAYY-20200316081851159.jpg"
                embed.set_image(url=player["picture"])
            embed.add_field(name='Character Name:',value=player["name"], inline=True)
            try:
                embed.add_field(name=str(player['current_health'])+'/'+str(player['total_health']),value="Health")
            except:
                player["current_health"] = 100
                player["total_health"] = 100
                embed.add_field(name=str(player['current_health'])+'/'+str(player['total_health']),value="Health",inline=False)
            try:
                embed.add_field(name='Damage:',value=player['damage'],inline=False)
            except:
                player['damage'] = 5
                embed.add_field(name='Damage:',value=player['damage'],inline=False)
            try:
                embed.add_field(name='Armor:',value=player['armor'],inline=False)
            except:
                player['armor'] = 5
                embed.add_field(name='Armor:',value=player['armor'],inline=False)
            embed.add_field(name='Gold:',value=player['gold'])

            embed.set_footer(text=f"Still under development? | {self.bot.user.name}")
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            await ctx.send(embed=embed)

    # start with giveGold command

def setup(bot):
    bot.add_cog(Character(bot))