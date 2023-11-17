import os
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(intents=intents, command_prefix='??')

@bot.command()
async def reset(ctx, extension):
    bot.unload_extension(f'components.{extension}')
    bot.load_extension(f'components.{extension}')
    await ctx.send(f'{extension} reloaded uwu *default fortnite dance* XDD')

for file in os.listdir('./main/components'):
    if file.endswith('.py'):
        bot.load_extension(f'components.{file[:-3]}')

bot.run(TOKEN)