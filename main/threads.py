import nextcord
from nextcord import Intents
from nextcord.ext import commands


my_intents = Intents.default()
my_intents.message_content = True
my_intents.messages = True
bot = commands.Bot(command_prefix='!7', intents=my_intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is all set.")

channel_list = [903596413231964191, 903596378293411891, 903596456466853969, 903596435663097907, 928645070134075462, 1143976152348770434]

@bot.event
async def on_message(message):
    if (message.author.bot):
        return 
    thread_name = "♥ Art Discussion ⦗{message.author.display_name}⦘"
    thread_message = "<a:wiggle:1021062305213071440> Use this thread to discuss art.\n\n**{message.author.display_name}**, if you want criticism on your artwork, head over to <#993147916548063295>! <:blureyes:996071212558061628>"
    if message.channel.id in channel_list:
        if (message.attachments) or message.content.endswith('.pnj'):
            thread_name = f"♥ Art Discussion ⦗{message.author.display_name}⦘"
            thread_message = f"<a:wiggle:1021062305213071440> Use this thread to discuss art.\n\n**{message.author.display_name}**, if you want criticism on your artwork, head over to <#993147916548063295>! <:blureyes:996071212558061628>"
            thread = await message.create_thread(name=thread_name,auto_archive_duration=60)
            await thread.send(thread_message)

@bot.event
async def on_message_delete(message):
    if message.channel.id in channel_list:
        thread = bot.get_channel(message.id)
        if thread is not None:
            await thread.delete()

#bot.run("OTkzMDY3MDk3MDQxMTU0MDQ4.GIhrSa.XUj4Eb-cMf5JXGOMgrfDyjsKSDedm1a5L3HAt0")
bot.run("MTAyMjQxOTY1MTA5NzAyMjUxNg.GDMlou.nNP6bhzF0NBl6PF8UCwv2qYWAweLPdICqXHNaI")