import nextcord
import os
import datetime
import random
import emoji
from asyncio import sleep
from nextcord.ext import commands, tasks

# GLOBAL VARIABLES
server = 903586180711481385
channels = [903596413231964191, 903596378293411891, 903596456466853969, 903596435663097907, 928645070134075462, 1143976152348770434]


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timeout.start()

    @tasks.loop(seconds=10)
    async def timeout(self):
        with open("spam_file", "w") as file:
            pass

    @commands.Cog.listener()
    async def on_message(self, msg):
        if len(msg.attachments) == 0 and msg.channel.id in channels and not msg.author.bot and not self.check_msg_for_img(msg):
            await self.checktimeout(msg)
            embed = nextcord.Embed(description="You can only post images in this channel. <:hehe:1013526129224732893>\n Use threads to discuss.",
                                   color=0xff4e6b)
            await msg.channel.send(embed=embed, delete_after=6)
            await sleep(2)
            await msg.delete()

    def check_msg_for_img(msg):
        img_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.webp', '.pnj']
        for ext in img_extensions:
            if msg.content.endswith(ext):
                return True
        return False

    async def checktimeout(self, msg):
        counter = 0
        with open("spam_file", "r+") as file:
            for lines in file:
                if lines.strip("\n") == str(msg.author.id):
                    counter += 1
            file.writelines(f"{str(msg.author.id)}\n")
            if counter > 3:
                await msg.author.timeout(datetime.timedelta(seconds=30), reason="Spamming")
                
    @nextcord.slash_command(description='Generate 3 random emojis', guild_ids=[server])
    async def randomemojis(
            self,
            interaction: nextcord.Interaction,
                          ):
            z = 0
            emoji_one_content, emoji_two_content, emoji_three_content = "", "", ""
            emoji_one, emoji_two, emoji_three = random.sample(range(0, 1663), 3)
            with open('emoji_file', 'r') as file:
                for emoji in file:
                    if z == emoji_one:
                        emoji_one_content = emoji
                    elif z == emoji_two:
                        emoji_two_content = emoji
                    elif z == emoji_three:
                        emoji_three_content = emoji
                    z += 1
            await interaction.response.send_message(content=f'{emoji_one_content} {emoji_two_content} {emoji_three_content}')  

def setup(bot):
    bot.add_cog(Misc(bot))