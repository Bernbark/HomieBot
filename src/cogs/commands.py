import discord
from discord.ext import commands
import platform
import random
import logging
import collections
from bson import ObjectId

import cogs._json #Imports the _json.py file which allows for blacklist read/write

adjectives = cogs._json.read_json("adjectives")
nouns = cogs._json.read_json("nouns")

class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def random_insult(self):
        adjective = random.choice(adjectives)
        noun = random.choice(nouns)
        return ' you '+adjective+' '+noun

    @commands.Cog.listener()
    async def on_ready(self):
        print("Commands Cog has been loaded\n-----")


    @commands.command()
    async def inspireme(self, ctx):
        number = random.randint(0,9)
        inspire = {0:'You suck',1:'Why try?',2:'Please don\'t ask me for inspiration',
                   3:'There is always someone who runs slower than you',
                   4:'You need more than a discord bot\'s help',
                   5:'Ask me when I\'m in the right mood',
                   6:'Seriously I am the wrong person to be asking for this.',
                   7:'OMG please stop asking me for help',
                   8:'Your hair will burn quickly in a fire',
                   9:'https://youtu.be/tYzMYcUty6s'}
        if number > 7:
            quote = random.choice(inspire)
        else:
            adj1 = random.choice(adjectives["adjectives"])
            adj2 = random.choice(adjectives["adjectives"])
            if adj1 == adj2:
                adj2 = random.choice(adjectives["adjectives"])
            charsToMatch=('a','e','i','o','u')

            if adj1.startswith(charsToMatch):
                quote = 'You are not at all an '+adj1+', '+adj2+' '+random.choice(nouns["nouns"])
            else:
                quote = 'You are not at all a '+adj1+', '+adj2+' '+random.choice(nouns["nouns"])
        embed = discord.Embed(title=f'~~~Daily Dose of Inspiration~~~',description='\uFEFF', color=random.choice(self.bot.color_list), timestamp=ctx.message.created_at)

        embed.add_field(name=f"{quote} |", value='\uFEFF')
        embed.add_field(name='Special thanks to Image for his help',value="HeLl YeAh")
        await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx):
        """
        A command that displays bot statistics
        """
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = ctx.guild.member_count

        embed = discord.Embed(title=f'{self.bot.user.name} Stats', description='\uFEFF', colour=ctx.author.colour, timestamp=ctx.message.created_at)

        embed.add_field(name='Bot Version:',value=self.bot.version)
        embed.add_field(name='Python Version:',value=pythonVersion)
        embed.add_field(name='Discord.Py Version:',value=dpyVersion)
        embed.add_field(name='Total Servers:',value=serverCount)
        embed.add_field(name='Total Users',value=memberCount)
        embed.add_field(name='Bot Developer',value="<@673664621521141781>")
        embed.add_field(name='Special thanks to Image for his help',value="HeLl YeAh")
        embed.set_footer(text=f"What are you doing stepdad? | {self.bot.user.name}")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(aliases=['disconnect', 'close', 'stopbot'])
    @commands.is_owner()
    async def logout(self, ctx):
        """
        If the user running the command owns the bot then this will disconnect the bot from discord.
        """
        await ctx.send(f"Hey {ctx.author.mention}, I am now logging out :wave:")
        await self.bot.logout()

    @commands.command()
    async def echo(self, ctx, *, message=None):
        """
        A simple command that repeats the users input back to them.
        """
        message = message or "Please provide the message to be repeated."
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    async def embed(self, ctx):
        """
        Displays an embedded image table
        """
        embedded = discord.Embed(
            title="the hottest bot around",
            color=discord.Color(0x3b12ef),
            description="This bot was made for the developer to learn python and server management",
            timestamp=ctx.message.created_at
        )

        embedded.add_field(
            name="If you have any suggestions please send them to Bernbark.",
            value="Thank you!~~~"
        )
        file = discord.File("C:\\Users\\Kory Stennett\\Desktop\\memes\\half fish.png", filename="image.png")
        embedded.set_image(url="attachment://image.png")

        await ctx.send(file=file,embed=embedded)


    @commands.command(aliases=['tbl'])
    @commands.is_owner()
    async def testBlacklist(self, ctx):


        if await self.bot.config.find(ctx.guild.id) is None:
            return
        server = await self.bot.config.find(ctx.guild.id)
        await ctx.send(server['blacklistedUsers'])

    @commands.command()
    @commands.is_owner()
    @commands.has_guild_permissions(manage_guild=True)
    async def blacklist(self, ctx, user: discord.Member):

        server = await self.bot.config.find(ctx.guild.id)
        try:
            blacklist = server['blacklistedUsers']
        except:
            blacklist = []
        blacklisted = user.id
        if ctx.message.author.id == user.id:
            await ctx.send("Hey, you cannot blacklist yourself!")
            return
        if blacklisted not in blacklist:
            blacklist.append(blacklisted)
            await self.bot.config.upsert({"_id":ctx.guild.id,'blacklistedUsers': blacklist})
            await ctx.send(f"Hey, I have blacklisted {user.name} for you.")
        else:
            await ctx.send(f"{user.name} is already blacklisted")

    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx, user: discord.Member):
        server = await self.bot.config.find(ctx.guild.id)
        if user.id not in server['blacklistedUsers']:
            return
        await self.bot.config.unset({"_id":ctx.guild.id, 'blacklistedUsers': user.id})
        await ctx.send(f"Hey, I have unblacklisted {user.name} for you.")

    @commands.command()
    async def DM(self, ctx, user: discord.User, *, message=None):
        """
        Type <prefix>DM @username MESSAGE to send a DM to a user
        """
        if message is None:
            message = "hey :)"
        embed = discord.Embed(title=f"Sent by {ctx.author.name}", desc='\uFEFF')
        embed.add_field(name="Personalized message: ",value=message)
        await user.send(embed=embed)
        await ctx.send("Message sent!")

    @commands.command(aliases=['number'])
    async def guess(self, ctx):
        server = await self.bot.config.find(ctx.guild.id)
        winner = ctx.author.id
        try:
            prefix = server['prefix']
        except:
            prefix = '-'
        await ctx.send(f'Hey, {ctx.author}! I\'m thinking of a number from 1 to 100. Try to guess which number! -1 to quit')
        number = random.randint(1, 100)
        loop_counter = 0
        while loop_counter < 7:
            answer = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if answer.content.startswith(prefix) and answer.content.isnumeric() is False:
                await ctx.send(f"Your message {answer.content} contains the prefix<{prefix}> for this server, exiting game to avoid conflict")
                print(str(answer.content))
                print(prefix)
                return
            try:
                answ = int(answer.content) # here it will try to return answer to a integer.
                print(answ)
                print(number)
                if answ == -1:
                    await ctx.send("Exiting game")
                    break
                if answ == number:
                    await ctx.send(f'Congrats {ctx.author}! You found the number.') # if user founds the answer, it will send a message and ends the loop.
                    leastTurns = loop_counter
                    try:
                        numberGameScores = server['numberGameScores']
                    except:
                        numberGameScores = ['Least Scores In Number Game']


                    if winner not in numberGameScores:
                        numberGameScores.append(str(winner)+' least turns for Number Guess Game= '+str(leastTurns+1))
                        await self.bot.config.upsert({"_id":ctx.guild.id,'numberGameScores': numberGameScores})

                    return
                else:
                    await ctx.send(f'Sorry, {ctx.author}, answer is higher.') if number-answ>0 else await ctx.send('Sorry, wrong answer. Answer is lower.')
                    loop_counter += 1
            except ValueError:
                await ctx.send(f'Please just type number {ctx.author}') # if it's not integer, then it will pass and send a warning.
                pass

        await ctx.send(f"Sorry, {ctx.author} couldn't find the answer. Answer was {number}")


def setup(bot):
    bot.add_cog(Commands(bot))