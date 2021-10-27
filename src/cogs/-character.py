from pymongo import MongoClient

import cogs._json

# Standard libraries
import os
import json
import logging
import datetime
import random
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
                                                  'current_xp': 0,
                                                  'needed_xp': 100,
                                                  'level': 1,
                                                  'damage': 5,
                                                  'armor': 5,
                                                  'backpack': [''],
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
                                              'current_xp': 0,
                                              'needed_xp': 100,
                                              'level': 1,
                                              'damage': 5,
                                              'armor': 5,
                                              'backpack': [''],
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
                embed.add_field(name='Health: '+str(player['current_health'])+'/'+str(player['total_health']),value='\uFEFF',inline=False)
            except:
                player["current_health"] = 100
                player["total_health"] = 100
                embed.add_field(name='Health: '+str(player['current_health'])+'/'+str(player['total_health']),value='\uFEFF',inline=False)
            embed.add_field(name='Experience: '+str(player['current_xp'])+'/'+str(player['needed_xp']),value='\uFEFF',inline=False)
            embed.add_field(name=f"Level **{player['level']}**",value='\uFEFF')
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
            embed = discord.Embed(title=f'{user.display_name}\'s Stats', description='\uFEFF', color=ctx.author.colour, timestamp=ctx.message.created_at)
            try:
                embed.set_image(url=player["picture"])
            except:
                player["picture"] = "https://cached.imagescaler.hbpl.co.uk/resize/scaleHeight/815/cached.offlinehbpl.hbpl.co.uk/news/SUC/MEMAYY-20200316081851159.jpg"
                embed.set_image(url=player["picture"])
            embed.add_field(name='Character Name:',value=player["name"], inline=True)
            try:
                embed.add_field(name='Health: '+str(player['current_health'])+'/'+str(player['total_health']),value='\uFEFF',inline=False)
            except:
                player["current_health"] = 100
                player["total_health"] = 100
                embed.add_field(name='Health: '+str(player['current_health'])+'/'+str(player['total_health']),value='\uFEFF',inline=False)
            embed.add_field(name='Experience: '+str(player['current_xp'])+'/'+str(player['needed_xp']),value='\uFEFF',inline=False)
            embed.add_field(name=f"Level **{player['level']}**",value='\uFEFF')
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
        name="restore",
        aliases=['rest','inn','heal'],
        description="Restores your health to full.",
        usage="Type <prefix>restore to heal fully"
    )
    async def restore(self, ctx):
        """
        Type <prefix>restore to heal to your max HP
        """
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)
        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create")
            return
        if player['gold'] < 50000:
            await ctx.send("You don't have the gold to heal, better go play games to earn more.")
        remainder = player['gold'] - 50000
        try:
            heal = player['total_health']
        except:
            player['current_health'] = heal = 100
            player['total_health'] = 100
        if player['current_health'] == player['total_health']:
            await ctx.send("You don't need to heal")
            return
        await self.bot.character.upsert({"_id": ctx.author.id, "current_health": heal, "gold": remainder})
        await ctx.send(f"Your health has been restored to {heal}! It cost 50000 gold.")

    @commands.command(
        name="gift",
        aliases=['goldgive','gg','send'],
        description="Send some of your gold to someone else who has a player profile",
        usage="Type <prefix>gift USER_NAME GOLD_AMOUNT to send gold"
    )
    async def gift(self, ctx, user: discord.Member, *, amount='0'):
        """
        Type <prefix>gift USER_NAME GOLD_AMOUNT to send gold
        """
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)
        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create")
            return
        try:
            other = await self.bot.character.find_by_id(user.id)
        except:
            other = None
        if other is None:
            await ctx.send("The player you're sending gold to doesn't have an account with me!")
            return
        try:
            number = int(amount)
        except ValueError:
            await ctx.send(f"{amount} needs to be an integer value")
            return
        if number > player['gold']:
            await ctx.send("Can't send more gold than you have!")
        if number < 1:
            await ctx.send("Can't send negative amounts of gold!")
            return
        if number == 0:
            await ctx.send("You must enter an amount to send!")
            return
        else:
            await self.bot.character.upsert({"_id": ctx.author.id, "gold": player['gold']-number})
            await self.bot.character.upsert({"_id": user.id, "gold": other['gold']+number})
            await ctx.send(f"You have sent {number} gold to {user.display_name}")

    @commands.command(
        name="inventory",
        aliases=['inv','items','item','bag'],
        description="Send some of your gold to someone else who has a player profile",
        usage="Type <prefix>inventory to see your items"
    )
    async def inventory(self, ctx):
        """
        Type <prefix>inv to see your items
        """
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)
        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create")
            return
        backpack = player['backpack']
        item_names = []
        for x in range(0,len(backpack)):
            item = await self.bot.items.find_by_id(int(backpack[x]))
            item_name = item['name']
            item_value = item['value']
            item_type = item['type']
            result = {
                'name':item_name,'value':item_value,'type':item_type
            }
            item_names.append(result)
        embed = discord.Embed(title=f"Inventory", description='\uFEFF', color=random.choice(self.bot.color_list))
        for x in item_names:
            name = x['name']
            value = x['value']
            type = x['type']

            embed.add_field(name=f"--- {name} ---",value=type+': '+str(value))
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Character(bot))