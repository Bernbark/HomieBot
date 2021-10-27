import discord
from pathlib import Path
import motor.motor_asyncio
from discord.ext import commands

class Shop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Shop Cog has been loaded\n-----")

    @commands.group(invoke_without_command=True,case_insensitive=True)
    async def shop(self, ctx):
        await ctx.send("This is the shop. Type <prefix>shop SHOP_TYPE to get to a certain variety of things to buy. Currently SHOP_TYPES include"
                       " 'stats'")

    @shop.group(invoke_without_command=True,case_insensitive=True)
    async def stats(self, ctx):
        await ctx.send("This is the Stats shop. You can buy stats using <prefix>shop stats armor/health/damage. I dunno why you'd want to though.")

    @stats.command(
        aliases=['hp']
    )
    async def health(self, ctx, *, amount=1):
        """
        -shop stats health AMOUNT_TO_BUY
        """
        if amount < 1 or amount > 50000:
            await ctx.send("You need to put a positive integer between 1-50000 for the amount to buy")
            return
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)
        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create in order to play")
            return
        if int(player['gold']) < amount*50000:
            await ctx.send("You don't have the gold to buy a damage upgrade. Costs 50,000 gold per health point")
            return
        else:
            cost = amount*50000
            try:
                await self.bot.character.upsert({"_id": ctx.author.id,
                                                 "total_health": player['total_health']+amount,
                                                 "gold": player['gold']-cost,
                                                 'current_health': player['total_health']+amount})
            except:
                player['total_health'] = 100+amount
                await self.bot.character.upsert({"_id": ctx.author.id,
                                                 "total_health": player['total_health']+amount,
                                                 "gold": player['gold']-cost,
                                                 'current_health': player['total_health']+amount})

            await ctx.send(f"You gained {amount} health! It cost {cost} gold.")

    @stats.command(
        aliases=['defense']
    )
    async def armor(self, ctx, *, amount=1):
        """
        -shop stats armor AMOUNT_TO_BUY
        """
        if amount < 1 or amount > 1000:
            await ctx.send("You need to put a positive integer between 1-1000 for the amount to buy")
            return
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)
        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create in order to play")
            return
        if int(player['gold']) < amount*1000000:
            await ctx.send("You don't have the gold to buy a damage upgrade. Costs 1 million gold")
            return
        else:
            cost = amount*1000000
            try:
                await self.bot.character.upsert({"_id": ctx.author.id, "armor": int(player['armor'])+amount,"gold":player['gold']-cost})
            except:
                player['defense'] = 5
                await self.bot.character.upsert({"_id": ctx.author.id, "armor": int(player['armor'])+amount,"gold":player['gold']-cost})
            cost = amount*1000000
            await ctx.send(f"You gained {amount} armor! It cost {cost} gold")

    @stats.command(
        aliases=['dmg']
    )
    async def damage(self, ctx, *, amount=1):
        """
        -shop stats damage AMOUNT_TO_BUY
        """
        if amount < 1 or amount > 1000:
            await ctx.send("You need to put a positive integer between 1-1000 for the amount to buy")
            return
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)
        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create in order to play")
            return
        if int(player['gold']) < amount*1000000:
            await ctx.send("You don't have the gold to buy a damage upgrade. Costs 1 million gold")
            return
        else:
            cost = amount*1000000
            try:
                await self.bot.character.upsert({"_id": ctx.author.id, "damage": int(player['damage'])+amount,"gold":player['gold']-cost})
            except:
                player['damage'] = 5
                await self.bot.character.upsert({"_id": ctx.author.id, "damage": int(player['damage'])+amount,"gold":player['gold']-cost})
            cost = amount*1000000
            await ctx.send(f"You gained {amount} damage! It cost {cost} gold")

def setup(bot):
    bot.add_cog(Shop(bot))