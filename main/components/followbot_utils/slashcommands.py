import nextcord
from nextcord.ext import commands
from nextcord.ext import application_checks

test_server = 903586180711481385

class Move(nextcord.ui.View):
    def __init__(self, page):
        super().__init__()
        self.value = None
        self.pg_number = 1
        self.pages = page

    @nextcord.ui.button(style=nextcord.ButtonStyle.grey, emoji='<:previous2:1015281584787685476>')
    async def first_page(
            self,
            button: nextcord.ui.Button,
            interaction: nextcord.Interaction,
    ):
        self.pg_number = 1
        await interaction.response.edit_message(embed=self.pages[0])

    @nextcord.ui.button(style=nextcord.ButtonStyle.grey, emoji='<:previous:1015281582900265084>')
    async def left_once(
            self,
            button: nextcord.ui.Button,
            interaction: nextcord.Interaction,
    ):
        if self.pg_number != 1:
            self.pg_number -= 1
            await interaction.response.edit_message(embed=self.pages[self.pg_number-1])
        else:
            return

    @nextcord.ui.button(style=nextcord.ButtonStyle.grey, emoji='<:next:1015281581788758098>')
    async def right_once(
            self,
            button: nextcord.ui.Button,
            interaction: nextcord.Interaction,
    ):
        if self.pg_number != 10:
            self.pg_number += 1
            await interaction.response.edit_message(embed=self.pages[self.pg_number-1])
            print(self.pg_number)
        else:
            print(self.pg_number)
            return

    @nextcord.ui.button(style=nextcord.ButtonStyle.grey, emoji='<:nenxt2:1015281580031361177>')
    async def last_page(
            self,
            button: nextcord.ui.Button,
            interaction: nextcord.Interaction,
    ):
        self.pg_number = len(self.pages)
        print(self.pg_number)
        await interaction.response.edit_message(embed=self.pages[self.pg_number-1])

class FollowBotSlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description='Set the channels of which will prompt notifications by default', guild_ids=[test_server])
    @application_checks.has_permissions(manage_messages=True)
    async def setup(
            self,
            interaction: nextcord.Interaction,
            channel: nextcord.abc.GuildChannel = nextcord.SlashOption(required=True,
                                                                      channel_types=[nextcord.ChannelType.text])
    ):
        fbot = self.bot.get_cog('FollowerBot')
        res = fbot.setupChannel(channel)
        if res.modified_count == 0 and res.upserted_id is None:
            await interaction.response.send_message(content='You already added this channel.', ephemeral=True)
        else:
            await interaction.response.send_message(content='Channel successfully added!', ephemeral=True)


    @nextcord.slash_command(description='Mute & Disable all art notifications in DMs')
    async def mutedms(
            self,
            interaction: nextcord.Interaction,
            mute: str = nextcord.SlashOption(
                name='',
                choices={"muted": 'True', "unmuted": "False"},
                required=True
            ),
    ):
        #fbot = self.bot.get_cog('FollowerBot')
        #fbot.checkForUser(interaction.user.id)
        #fbot.updateDB(interaction.user.id, {'$set': {'mute_dm': mute}})
        #await interaction.response.send_message(content='Your choice has been remembered. <a:wiggleCRAZY:1008697272474816583>', ephemeral=True, delete_after=60)
        #print(f'(FollowBot) {interaction.user} mute DM: {mute}')
        fbot = self.bot.get_cog('FollowerBot')
        fbot.checkForUser(interaction.user.id)
        fbot.updateDB(interaction.user.id, {'$set': {'mute_dm': mute}})
        content = ''
        if mute == 'True':
            content = "OK. You'll no longer get DMs when people post art. <a:awhyyy:1009933899499057172>"
        else:
            content = "OK. You'll get DMs again when people post art. Nice."
        await interaction.response.send_message(content=content, ephemeral=True, delete_after=60)
        print(f'(FollowBot) {interaction.user} mute DM: {mute}')

    @nextcord.slash_command(description='Show leaderboard', guild_ids=[test_server])
    async def leaderboard(
            self,
            interaction: nextcord.Interaction,
                          ):
        fbot = self.bot.get_cog('FollowerBot')
        fbot.checkForUser(interaction.user.id)
        page = await fbot.getLeaderboard(interaction)
        view = Move(page)
        await interaction.response.send_message(embed=page[0], view=view)
        
    @nextcord.slash_command(description='Set certain channels to disable art notifications from!', guild_ids=[test_server])
    async def ignorechannel(
            self,
            interaction: nextcord.Interaction,
            channel: nextcord.abc.GuildChannel = nextcord.SlashOption(required=True,
                                                                      channel_types=[nextcord.ChannelType.text]),
            enable: str = nextcord.SlashOption(
                name='ignore',
                choices={"unignore": 'False', "ignore": 'True'},
                required=True
            )
    ):
        fbot = self.bot.get_cog('FollowerBot')
        fbot.checkForUser(interaction.user.id)
        if enable == 'True':
            res = await fbot.slashignorechannel(interaction.user.id, channel)
            await interaction.response.send_message(content=res, ephemeral=True, delete_after=60)
        else:
            res = await fbot.unignorechannel(interaction.user.id, channel)
            await interaction.response.send_message(content=res, ephemeral=True)

    @nextcord.slash_command(description='Unfollow someone', guild_ids=[test_server])
    async def unfollow(
            self,
            interaction: nextcord.Interaction,
            user: nextcord.User
    ):
        fbot = self.bot.get_cog('FollowerBot')
        res = await fbot.slashunfollow(user, interaction.user.id)
        await interaction.response.send_message(content=res, ephemeral=True, delete_after=60)

    @nextcord.slash_command(description='Follow someone. This means you get DM notifications when they post art.', guild_ids=[test_server])
    async def follow(
            self,
            interaction: nextcord.Interaction,
            user: nextcord.User
    ):
        fbot = self.bot.get_cog('FollowerBot')
        res = await fbot.slashfollow(user, interaction.user.id)
        if type(res) == int:
            embed = await fbot.buildFollowEmbed(res)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=60)
            print(f'{interaction.user} followed {user}')
        else:
            await interaction.response.send_message(content=res, ephemeral=True, delete_after=60)
            print(f'{interaction.user} tried follow {user}')

    @nextcord.slash_command(description='Opt in or out of the system. Its ON by default!')
    async def opt(
            self,
            interaction: nextcord.Interaction,
            opt: str = nextcord.SlashOption(
                name='',
                choices={'in': 'Enabled', 'out': 'Disabled'}
            ),
    ):
        fbot = self.bot.get_cog('FollowerBot')
        fbot.checkForUser(interaction.user.id)
        fbot.updateDB(interaction.user.id, {'$set': {'opt': opt}})
        content = ''
        if opt == 'Enabled':
            content = '**Opted in**, anyone in the server can follow you now.'
        else:
            content = '**Opted out**, no one can follow you now, you keep your current followers tho!'
        await interaction.response.send_message(content=content, ephemeral=True, delete_after=60)
        print(f'{interaction.user} optin: {opt}')

def setup(bot):
    bot.add_cog(FollowBotSlashCommands(bot))