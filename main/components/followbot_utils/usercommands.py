import nextcord
from nextcord.ext import commands

test_server = 903586180711481385

class FollowBotUserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.user_command(guild_ids=[test_server])
    async def unfollow(
            self,
            interaction: nextcord.Interaction,
            member: nextcord.Member
    ):
        fbot = self.bot.get_cog('FollowerBot')
        if fbot.checkForUser(interaction.user.id):
            res = fbot.updateDB(interaction.user.id, {'$pull': {'following': member.id}})
            if res.modified_count == 0:
                await interaction.response.send_message(content='You are not following this user!', ephemeral=True)
                print(f'{interaction.user} tried to unfollow {member} | user command')
                return
            fbot.updateDB(member.id, {'$inc': {'follower_count': -1}})
            user = await self.bot.fetch_user(member.id)
            await interaction.response.send_message(content=f'You unfollowed {user.mention} <:catOK:993819099023036456>',
                                                    ephemeral=True)
            print(f'(FollowBot) {interaction.user} unfollowed {member} | user command')
        else:
            await interaction.response.send_message(content="You're not following anyone yet. You could though, using </follow:1015342375360540753>", ephemeral=True
                                                    , delete_after=60)
            print(f'(FollowBot) {interaction.user} unfollow {member} | user command')

    @nextcord.user_command(guild_ids=[test_server])
    async def follow(
            self,
            interaction: nextcord.Interaction,
            member: nextcord.Member
    ):
        fbot = self.bot.get_cog('FollowerBot')
        res = await fbot.slashfollow(member, interaction.user.id)
        if type(res) == int:
            embed = await fbot.buildFollowEmbed(res)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=60)
            print(f'{interaction.user} followed {member} | user command')
        else:
            await interaction.response.send_message(content=res, ephemeral=True, delete_after=60)
            print(f'{interaction.user} tried follow {member} | user command')


def setup(bot):
    bot.add_cog(FollowBotUserCommands(bot))