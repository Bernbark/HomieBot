import discord
from discord.ext import commands

class Groups(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("SubCommands Cog has been loaded\n-----")

    @commands.group(invoke_without_command=True)
    async def first(self, ctx):
        await ctx.send("This is the first command layer")

    @first.group(invoke_without_command=True)
    async def second(self, ctx):
        await ctx.message.author.send("Hey, I like your bazingas")

    @second.command()
    async def third(self, ctx, channelId=None):
        """
        This command requires a channel ID to be pasted after third
        -first second third CHANNELID
        """
        if channelId is not None:
            channel = self.bot.get_channel(int(channelId))
            await channel.send("Hey! This is a message from me the bot. Who possibly ran this command?", delete_after=15)

def setup(bot):
    bot.add_cog(Groups(bot))