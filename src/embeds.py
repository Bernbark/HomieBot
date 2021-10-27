from datetime import datetime

import ctx as ctx
import discord

embed = discord.Embed(
    title="the hottest bot around",
    color=discord.Color(0x3b12ef),
    description="This bot was made for the developer to learn python and server management",
    timestamp=datetime.datetime.utcfromtimestame(1580842764)
)

embed.add_field(
    name="If you have any suggestions please send them to Bernbark.",
    value="Thank you!~~~"
)
embed.set_image(url="https://tenor.com/bkz5z.gif")
embed.set_thumbnail(url="https://tenor.com/7jGZ.gif")

await ctx.send(
    content="This is a normal message to be sent alongside the embed",
    embed=embed
)

"""
If I want to send a local file as the embed image:
embed = discord.Embed()
embed.set_image(
    url="attachment://hello.png"
)
image = discord.File("hello.png")
await ctx.send(
    embed=embed
    file=image
)
"""