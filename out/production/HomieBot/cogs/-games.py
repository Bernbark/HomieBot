import asyncio
import time
import discord
import datetime
from discord.ext import commands
from discord.ext import tasks
import platform
import random


gameLoopTime = 20

arithmetic = ['+',
              '-',
              '*']
def new_equation_easy():
    first = random.randint(1,10)
    second = random.randint(1,10)
    sign = random.choice(arithmetic)
    if sign is '+':
        return {'equation':str(first)+sign+str(second),'answer':first+second}
    elif sign is '-':
        return {'equation':str(first)+sign+str(second),'answer':first-second}
    else: # '*' multiply
        return {'equation':str(first)+sign+str(second),'answer':first*second}

def new_equation_hard():
    first = random.randint(1,100)
    second = random.randint(1,100)
    sign = random.choice(arithmetic)
    if sign is '+':
        return {'equation':str(first)+sign+str(second),'answer':first+second}
    elif sign is '-':
        return {'equation':str(first)+sign+str(second),'answer':first-second}
    else: # '*' multiply
        return {'equation':str(first)+sign+str(second),'answer':first*second}
#Class of Games written from scratch by Kory Stennett for Homie Bot
class Games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.last_timeStamp = datetime.datetime.utcfromtimestamp(0)


    @commands.command(
        name="mathwiz",
        aliases=['math','wiz','m'],
        description="Answer the questions for gold, but costs gold to enter.",
        usage="Plays a math game.",
    )
    async def mathwiz(self, ctx, *, bet='10'):
        """
        Type <prefix>m BET_AMOUNT You can play by betteng a certain amount or just typing <prefix>m spends 10 gold to play
        """
        winnings = int(bet)*2
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)
        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create in order to play")
            return
        if int(player['gold']) < 10 or int(bet) > int(player['gold']):
            await ctx.send("You don't have the gold to play this game, must fight in battles to earn more or bet less.")
            return
        else:
            bid = int(bet)
            currentGold = int(player['gold'])
            await self.bot.character.upsert({"_id":ctx.author.id,'gold': player['gold']+(-1*bid)})
            await ctx.send("Welcome to Math Wizard. You will be asked to solve the equation in the allotted time or lose your gold."
                           " Your 20 second timer starts now, but you only have 3 seconds to answer each question."
                           " Failure to answer in time results in an 3 second penalty"
                           " Bet more than 1000 to go to hard mode.")
            if bid > 1000:
                data = new_equation_hard()
            else:
                data = new_equation_easy()
            equation = data['equation']
            answer = data['answer']
            await ctx.send(equation)

            counter = 0
            correct = 0
            while counter <= gameLoopTime:
                try:
                    choice = await self.bot.wait_for('message',timeout=3.8, check=lambda message: message.author == ctx.author)


                    if str(choice.content) == str(answer):
                        correct+=1
                        if bid > 1000:
                            data = new_equation_hard()
                        else:
                            data = new_equation_easy()
                        equation = data['equation']
                        answer = data['answer']
                        counter+=2
                        time_left = gameLoopTime-counter
                        if time_left > 0:
                            await ctx.send(f"Keep moving, time left: {time_left} seconds, next equation: {equation}")
                        else:
                            await ctx.send(f"Time is almost out, get your last answer in! Equation: {equation}")

                        await self.bot.character.upsert({"_id":ctx.author.id,'gold': currentGold-bid+winnings})
                    else:
                        if bid > 1000:
                            data = new_equation_hard()
                        else:
                            data = new_equation_easy()
                        equation = data['equation']
                        answer = data['answer']
                        counter+=2
                        time_left = gameLoopTime-counter
                        await ctx.send(f"Sorry, wrong, time left: {time_left} seconds, next one: {equation}")

                except asyncio.TimeoutError:
                    counter += 3
                    time_left = gameLoopTime-counter
                    await ctx.send(f"3 second penalty for no answer in time. Time left {time_left} seconds.")

            if correct > 0:
                multi = correct*winnings
                await ctx.send(f"Time up! You got {correct} correct. You earned {winnings} points. Multiply by the number correct to get {multi} gold.")
                await self.bot.character.upsert({"_id":ctx.author.id,'gold': currentGold-bid+(winnings*correct)})
            elif correct == 0:
                await ctx.send(f"You probably didn't answer in time, you lose all bet money in the process")
            else:
                await ctx.send(f"Sorry, you lose {bet} gold. You couldn't get any answers right. Try again!")

    @commands.command(
        name="flip",
        aliases=['f','toss','coin'],
        description="Flip a coin, heads you win twice your money back, tails you lose everything you bet.",
        usage="Do <prefix>flip BET_AMOUNT to play, max bet of 100,000",
    )
    async def flip(self,ctx,*,bet='1'):
        try:
            winnings = int(bet)*2
        except ValueError:
            await ctx.send(f"You must bet with a number, {bet} is not a number")
            bet = '0'
            winnings = int(bet)*2
        if int(bet) < 1 and int(bet)!= 0:
            await ctx.send("You can't bet less than 1 coin.")
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)
        except:
            player = None
        if winnings is 0:
            return
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create in order to play")
            return
        if int(player['gold']) < 1 or int(bet) > int(player['gold']) or int(bet) > 100000:
            await ctx.send("You don't have the gold to play this game or you bet more than 100,000, must fight in battles to earn more or bet less.")
            return
        else:
            bid = int(bet)
            currentGold = int(player['gold'])
            await self.bot.character.upsert({"_id":ctx.author.id,'gold': player['gold']+(-1*bid)})
            flip = random.randint(1,2)
            if flip == 1:
                await ctx.send(f"You win the coin toss! Gain {winnings} gold!")
                await self.bot.character.upsert({"_id":ctx.author.id,'gold': currentGold-bid+winnings})
            else:
                await ctx.send(f"You lost the coin toss as well as your bet of {bet} gold!")

    @commands.command(
        name="trivia",
        aliases=['t','triv','quiz'],
        description="You will be asked 5 questions and be rewarded for the ones you get right.",
        usage="Do <prefix>trivia to play"
    )
    async def trivia(self,ctx):

        return


def setup(bot):
    bot.add_cog(Games(bot))