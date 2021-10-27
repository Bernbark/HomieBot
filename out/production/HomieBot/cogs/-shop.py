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
        await ctx.send("This is the shop. Type <prefix>shop SHOP_TYPE to get to a certain variety of things to buy.")

    @shop.group(invoke_without_command=True,case_insensitive=True)
    async def stats(self, ctx):
        await ctx.send("This is the Stats shop. You can buy stats using <prefix>shop stats armor/health/damage. I dunno why you'd want to though.")



    @stats.command(
        aliases=['defense']
    )
    async def armor(self, ctx, *, amount=1):
        """
        This command requires a channel ID to be pasted after third
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
            try:
                await self.bot.character.upsert({"_id": ctx.author.id, "armor": int(player['armor'])+amount})
            except:
                player['armor'] = 5
                await self.bot.character.upsert({"_id": ctx.author.id, "armor": int(player['armor'])+amount})
            await ctx.send(f"You gained {amount} armor!")

    @stats.command(
        aliases=['dmg']
    )
    async def damage(self, ctx, *, amount=1):
        """
        This command requires a channel ID to be pasted after third
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
            try:
                await self.bot.character.upsert({"_id": ctx.author.id, "damage": int(player['damage'])+amount})
            except:
                player['damage'] = 5
                await self.bot.character.upsert({"_id": ctx.author.id, "damage": int(player['damage'])+amount})
            await ctx.send(f"You gained {amount} damage!")

def setup(bot):
    bot.add_cog(Shop(bot))