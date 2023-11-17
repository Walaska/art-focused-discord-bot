import nextcord
import os
import random
import requests
from nextcord.ext import commands

# GLOBAL VARRIABLES
server = 903586180711481385
channel = 1031229812985057350

class Bannerbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Banner bot online!')
        await self.changeBanner()

    async def changeBanner(self):
        guild = await self.bot.fetch_guild(server)
        images = []
        chnl = await self.bot.fetch_channel(channel)
        messages = await chnl.history(limit=100).flatten()
        for msg in messages:
            if msg.attachments != []:
                images.append(msg.attachments)
        x = random.randint(1, len(images)) - 1
        img = await images[x][0].save(fp=images[x][0].filename)
        with open(f'./{images[x][0].filename}', 'rb') as image:
            await guild.edit(banner=image.read())
        os.remove(f'./{images[x][0].filename}')

def setup(bot):
    bot.add_cog(Bannerbot(bot))