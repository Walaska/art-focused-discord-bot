import datetime
import nextcord
import os
from nextcord.ext import commands
from nextcord.ext import application_checks

# GLOBAL VARIABLES
server = 903586180711481385
channel = 979374616311136326 # ID OF JOIN-LEAVE CHANNEL
role = 980449409865244682 # MOD ROLE ID

class Banbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ban bot online!')

    @nextcord.slash_command(description='Ban members that joined x minutes ago.', guild_ids=[server])
    @application_checks.has_permissions(manage_messages=True)
    async def exterminate(
            self,
            interaction: nextcord.Interaction,
            time: float,
            reason: str,
        ):
        """
        Parameters
        ----------
        interaction: Interaction
            The interaction object
        time: float
            How many MINUTES. Number required.
        reason: str
            What is the reason for this action might I ask???
        """
        if time > 1440 or time < 0:
        	await interaction.response.send_message(content="Invalid time!", ephemeral=False, delete_after=60)
        else:
            i = 0
            mod_role = interaction.guild.get_role(role)
            delete_time = datetime.datetime.now() - datetime.timedelta(minutes=time)
            join_channel = await self.bot.fetch_channel(channel)
            async for message in join_channel.history(limit=500, after=delete_time):
                if interaction.guild.get_member(message.author.id) == None:
                    await message.guild.ban(message.author, reason=reason, delete_message_days=7)
                    print(message.author)
                    i += 1                    
                elif mod_role not in message.author.roles and not message.author.bot:
                    await message.guild.ban(message.author, reason=reason, delete_message_days=7)
                    print(message.author)
                    i += 1
            await interaction.response.send_message(content=f"{i} Insects exterminated!", ephemeral=False, delete_after=60)

def setup(bot):
    bot.add_cog(Banbot(bot))