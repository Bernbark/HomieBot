import discord
from pathlib import Path
import motor.motor_asyncio
from discord.ext import commands
from discord.ext import tasks
import random
# Local code
import utils.json_loader
from utils.mongo import Document
import asyncio

firstName = [
    'Grabby',
    'Crabby',
    'Agitated',
    'Pissed-off',
    'Greased-up',
    'Berserk'
]

lastName = [
    'Handsman',
    'Lobster',
    'Bully',
    'American',
    'Mohawk-user',
    'Simp'
]

attack = [
    'a',
    'attack',
    'fight',
    'f',
    'battle'
]

defense = [
    'd',
    'defense',
    'defend',
    'block',
    'b',
    'guard'
]

attack_p =['Giant','Massive','Giga','Power']
defense_p =['Fortified','Diamond-Encrusted','Titanium']

attack_s =['of Malice','of Pain','of Caliber']
defense_s=['of Defense','of Fortitude','of Protection']

attack_n=['Sword','Axe','Bow']
defense_n=['Shield','Greaves','Chestplate','Helmet','Kilt']


def itemMake(level):

    choice = 1
    if choice == 1:
        r_no = random.randint(1,2)
        if r_no == 1:
            name = random.choice(attack_p)+' '+random.choice(attack_n)+' '+random.choice(attack_s)
            type = 'attack'
        else:
            name = random.choice(defense_p)+' '+random.choice(defense_n)+' '+random.choice(defense_s)
            type = 'defense'

        value = random.randint(1*level,3*level)
        item = {
            'name':name,
            'value':value,
            'type':type
        }
        return item
    else:

        item = 'No'
        return item

def enemy(level):

    _enemy = dict();
    _enemy['defense'] = random.randint(1*level, 3*level)
    _enemy['attack'] = 10 + random.randint(1*level, 3*level)
    _enemy['xp'] = 15*level-random.randint(1*level,3*level)
    _enemy['health'] = 10*level+random.randint(1*level,3*level)
    name1 = random.choice(firstName)
    name2 = random.choice(lastName)
    _enemy['name'] = name1+' '+name2
    return _enemy

class Battle(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="battle",
        aliases=['fight'],
        description="Fight against enemies for gold and rewards. Enemy strength will be based on your current level.",
        usage="Type <prefix>battle and you will be launched into a fight",
        case_insensitive=True
    )
    async def battle(self, ctx):
        server = await self.bot.config.find(ctx.guild.id)
        player = await self.bot.character.find(ctx.author.id)
        try:
            prefix = server['prefix']
        except:
            prefix = '-'
        try:
            player = await self.bot.character.find_by_id(ctx.author.id)
        except:
            player = None
        if player is None:
            await ctx.send("You don't have a character profile yet. Create one with <prefix>create in order to fight")
            return
        fightCost = 5000*player['level']
        if int(player['current_health']) < 1 or player['gold'] < fightCost:
            await ctx.send("You don't have the gold to unlock the gates of battle, play mathwiz to get some more gold")
            return
        else:
            stop = 0
            p_level = player['level']
            player_dmg = player['damage']
            player_def = player['armor']
            player_hp = player['current_health']
            _enemy = enemy(player['level'])
            enemy_dmg = _enemy['attack']
            enemy_def = _enemy['defense']
            enemy_health = _enemy['health']
            eName = _enemy['name']
            await ctx.send(f"You are attacked by a {eName}. Type fight or defend to battle, no prefixes during battle. Type quit to quit")
            while enemy_health > 0 and player_hp > 0:
                choice = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                if choice.content.startswith('quit'):
                    await ctx.send("Exiting game, you will lose your gold.")
                    return
                if choice.content.startswith(prefix):
                    wrong = True
                    while wrong is True:
                        await ctx.send("No use of prefixes")
                        choice = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if choice.content.startswith(prefix):
                            wrong = True
                        else:
                            wrong = False
                if choice.content.lower() in attack:
                    p_attack = player_dmg-enemy_def+random.randrange(-2*player['level'],2*player['level'])
                    if p_attack < 0:
                        p_attack = 0
                    e_attack = enemy_dmg-player_def+random.randrange(-2*player['level'],2*player['level'])
                    if e_attack < 0:
                        e_attack = 0
                    enemy_health-=p_attack
                    player_hp-=e_attack
                    if player_hp < 0:
                        player_hp = 0
                    if enemy_health < 0:
                        enemy_health = 0
                    await ctx.send(f"You dealt {p_attack} damage and received {e_attack} damage. You have {player_hp} health remaining, enemy has {enemy_health} health remaining")
                elif choice.content.lower() in defense:
                    player_hp-=(enemy_dmg/2)-player_def
                    await ctx.send(f"You defended {eName}'s attack. Took {(enemy_dmg/2)-player_def} damage")
                else:
                    await ctx.send(f"Make a valid selection. Attack/defend")
            if enemy_health == 0:
                item = itemMake(p_level)
                print(item)
                if item is not "No":
                    item_name = item['name']
                    item_value = item['value']
                    item_type = item['type']
                    item_amount = await self.bot.items.get_all();
                    item_no = len(item_amount)+1
                    product = {
                        '_id':item_no,
                        'name':item_name,
                        'value':item_value,
                        'type':item_type
                    }
                    try:
                        backpack = player['backpack']
                    except:
                        backpack = []
                    backpack.append(str(item_no))

                    await self.bot.character.upsert({"_id": ctx.author.id,"backpack": backpack})
                    await self.bot.items.upsert(product)
                    await ctx.send("You found a "+item_name)
                await ctx.send("You won the battle!")
            else:
                await ctx.send("You died, you earn nothing for this fight")

def setup(bot):
    bot.add_cog(Battle(bot))