import os
import nextcord
import math
import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
from urllib import request
from urllib.request import Request, urlopen
from PIL import Image, ImageFilter
from nextcord.ext import commands, tasks

db_url = f"mongodb+srv://neyasbot:rtv7uxHIwWkiIiwb@digitalart.k4xqkao.mongodb.net/?retryWrites=true&w=majority"
cluster = MongoClient(db_url)
db = cluster["followerbot"]
collection = db["follow_cons"]

class FollowerBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels: [] = self.getAllowedChannels()
        try:
            bot.load_extension('components.followbot_utils.slashcommands')
            bot.load_extension('components.followbot_utils.usercommands')
        except Exception:
            bot.reload_extension('components.followbot_utils.slashcommands')
            bot.reload_extension('components.followbot_utils.usercommands')
        self.cooldown = []
        self.pages = []
        self.checkLeavers()
        self.cooldown_timer.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Follower bot wörking!')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = self.getData({ '_id': member.id })
        if data is None:
            self.checkForUser(member.id)
            return
        else:
            self.updateDB(member.id, {'$set': {'left': 'rejoined'}})

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        date = datetime.today()
        self.checkForUser(member.id)
        self.updateDB(member.id, {'$set': {'left': date}})

    @commands.Cog.listener()
    async def on_message(self, msg):
        if len(msg.attachments) > 0 and msg.channel.id in self.channels and not self.checkCooldowns(msg.author.id):
            if await self.getUsersToSendDM(msg) is False:
                return
            self.addImageCount(msg.author, msg.channel)

    def checkLeavers(self):
        date = datetime.today()
        thirty_days_ago = date - timedelta(days=30)
        x = collection.delete_many( { 'left': { '$lt': thirty_days_ago} } )
        print('User deletion complete')
        print('Deleted count:')
        print(x.deleted_count)

    @tasks.loop(seconds=1)
    async def cooldown_timer(self):
        date = datetime.today()
        ten_seconds = date - timedelta(seconds=10)
        if len(self.cooldown) != 0:
            for i in self.cooldown:
                if i['cd'] <= ten_seconds:
                    new_list = filter(lambda x: x.get('id')!=i['id'], self.cooldown)
                    self.cooldown = list(new_list)

    def addImageCount(self, user, channel):
        self.checkForUser(user.id)
        self.updateDB(user.id, {'$inc': {'image_count': 1, f'{channel.id}': 1}})

    async def getUsersToSendDM(self, msdata):
        data = collection.find({ 'following': msdata.author.id })
        ct = self.blurImage(msdata.attachments[0].url)
        if ct is False:
            return False
        embed = await self.buildDMEmbed(msdata, ct)
        user = None
        for x in data:
            if x['mute_dm'] != 'True' and msdata.channel.id not in x['channels']:
                try:
                    with open(f'./blur_img.{ct}', 'rb') as fp:
                        user = await self.bot.fetch_user(x['_id'])
                        await user.send(file=nextcord.File(fp, f'img.{ct}'), embeds=embed)
                        print(f'(FollowBot) DM sent successfully to {user}')
                except Exception as e:
                    print(f'(FollowBot) Something went wrong when sending DMs to {user}')
                    print(e)
            else:
                return False
        os.remove(f'./blur_img.{ct}')
        date = datetime.today()
        self.cooldown.append({'id': msdata.author.id, 'cd': date})

    # async def walas(self):
    #    g = self.bot.get_guild(903586180711481385)
    #    for member in g.members:
    #        self.checkForUser(member.id)
    #    print('Walas function done')

    def getLeaderboardPos(self, interaction):
        all_users_count = interaction.guild.member_count
        data = collection.find().sort('follower_count', -1)
        pos = 0
        for x in data:
            if x['_id'] == interaction.user.id:
                return f'{pos+1} of {all_users_count - 1}'
            else:
                pos += 1
        return '-1 of -1'

    async def getLeaderboard(self, interaction):
        self.pages = []
        yt = 'https://www.youtube.com/watch?v=5YG_oKPJ7Iw&t=20s'
        data = list(collection.find().sort('follower_count', -1).limit(100))
        pos_string = self.getLeaderboardPos(interaction)
        max_pages = math.ceil((len(data)) / 10)
        first_user = await self.bot.fetch_user(data[0]['_id'])
        count, pg_number = 0, 0
        str, user = '', ''
        for x in range(len(data)):
            if count != 10:
                if data[x]['_id'] != 3306:
                    temp = self.bot.get_user(data[x]['_id'])                   
                    follower_count = data[x]['follower_count']
                    if temp == None:
                        user = 'Unknown'
                        str += f'`{x+1}. |` **Unknown** — **[{follower_count}]({yt})**\n'
                    else:
                        user = temp
                        str += f'`{x+1}. |` **{user.name}** — **[{follower_count}]({yt})**\n'
                    count += 1
            else:
                pg_number += 1
                page = self.buildPage(str, pos_string, interaction, pg_number, first_user, max_pages)
                self.pages.append(page)
                str = ''
                count = 1
                if data[x]['_id'] != 3306:
                    temp = self.bot.get_user(data[x]['_id'])
                    follower_count = data[x]['follower_count']
                    if temp == None:
                        user = 'Unknown'
                        str += f'`{x+1}. |` **Unknown** — **[{follower_count}]({yt})**\n'
                    else:
                        user = temp
                        str += f'`{x+1}. |` **{user.name}** — **[{follower_count}]({yt})**\n'
        pg_number += 1
        page = self.buildPage(str, pos_string, interaction, pg_number, first_user, max_pages)
        self.pages.append(page)
        return self.pages

    def buildPage(self, str, pos_info, interaction, page_number, first_user, max_pages):
        embed = nextcord.Embed(title='Follower leaderboard', description=str, color=0xff4e6b)
        embed.set_author(name='Followers',
                         icon_url='https://cdn.discordapp.com/attachments/978921288238243841/'
                                  '1015260832025825330/follower.png')
        embed.set_thumbnail(url=first_user.display_avatar.url)
        embed.set_footer(text=f'Your position: {pos_info} | Page {page_number}/{max_pages}',
                         icon_url=interaction.user.display_avatar.url)
        return embed

    def checkCooldowns(self, userid):
        if len(self.cooldown) != 0:
            for i in self.cooldown:
                if i['id'] == userid:
                    return True
            return False
        else:
            return False

    def blurImage(self, imageurl):
        img_data = requests.get(imageurl).content
        r = requests.head(imageurl)
        content_type = r.headers['content-type']
        ct = content_type.split('/')[1]
        if ct not in ['jpg', 'png', 'jpeg']:
            print('Content type error:')
            print(content_type)
            return False
        with open(f'user_img.{ct}', 'wb') as handler:
            handler.write(img_data)
        img = Image.open(f'./user_img.{ct}')
        blur_img = img.filter(ImageFilter.GaussianBlur(15))
        blur_img.save(f'./blur_img.{ct}')
        os.remove(f'./user_img.{ct}')
        return ct

    def getAllowedChannels(self):
        data = self.getData({ '_id': 3306 })
        if data is None:
            return []
        else:
            return data['channel_ids']

    def setupChannel(self, channel):
        self.channels.append(channel.id)
        return self.updateDB(3306, {'$addToSet': {'channel_ids': channel.id}})

    async def buildDMEmbed(self, msdata, ct):
        embeds = []
        date = datetime.today().strftime('%d/%m/%Y')
        embed = nextcord.Embed(color=0xff4e6b)
        embed.set_image(url=f'attachment://img.{ct}')
        embed.set_author(name=f"new art just dropped. Go take a peek.",
                         icon_url=msdata.author.display_avatar.url)
        embed.add_field(name="\u200B", value=f"{msdata.author.mention} just posted this in {msdata.channel.mention}\n "
                        f"[Jump to image]({msdata.jump_url})",
                        inline=False)
        embed.set_footer(text=f'✉️ sent from DigitalArt | {date}')
        embeds.append(embed)

        #Second Embed
        second_embed = nextcord.Embed(color=0xff4e6b, description=("**Don't want these DMs anymore?** Use </mutedms:1076235839836803193>."))
        embeds.append(second_embed)
        return embeds

    async def buildFollowEmbed(self, userid):
        user = await self.bot.fetch_user(userid)
        followers = self.getfollowers(userid)
        embed = nextcord.Embed(color=0xff4e6b)
        embed.set_footer(text="/help to learn more",
                            icon_url="https://cdn.discordapp.com/attachments/"
                                    "1000861249963311204/1003057966125166623/temp_new_icon.png")
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name=f"{user} follower count: {followers}",
                        value=f"You followed: {user.mention}, nice. <a:ppupvoteparrot:1009625872657039381>", inline=False)
        return embed

    async def slashignorechannel(self, interactionid, channel):
        res = self.updateDB(interactionid, {'$addToSet': {'channels': channel.id}})
        if res.modified_count == 0:
            u = await self.bot.fetch_user(interactionid)
            print(f'(FollowBot) {u} tried to ignore {channel} channel yet they already do ignore it :D')
            return 'You ignored this channel already, silly.'
        u = await self.bot.fetch_user(interactionid) 
        print(f'(FollowBot) {u} ignored {channel} channel')
        return f"You'll no longer receive notifications from images posted in `#{await self.bot.fetch_channel(channel.id)}` channel."

    async def unignorechannel(self, interactionid, channel):
        res = self.updateDB(interactionid, {'$pull': {'channels': channel.id}})
        if res.modified_count == 0:
            u = await self.bot.fetch_user(interactionid)
            print(f'(FollowBot) {u} tried to unignore {channel} channel but they did not ignore it before')
            return 'You havent ignored this channel. :O'
        u = await self.bot.fetch_user(interactionid)
        print(f'(FollowBot) {u} unignored {channel.mention} channel')
        return f'You unignored {channel.mention}'

    async def slashunfollow(self, user, interactionid):
        if user.id == interactionid:
            print(f'(FollowBot) {user} tried to unfollow themselves')
            return "Nice try, but you can't follow yourself, nerd. <a:wiggleCRAZY:1008697272474816583>"
        if self.checkForUser(interactionid):
            res = self.updateDB(interactionid, {'$pull': {'following': user.id}})
            if res.modified_count == 0:
                u = await self.bot.fetch_user(interactionid)
                print(f'(FollowBot) {u} tried to unfollow {user} without following them :D')
                return "You aren't following this user!"
            self.updateDB(user.id, {'$inc': {'follower_count': -1}})
            u = await self.bot.fetch_user(interactionid)
            print(f'(FollowBot) {u} unfollowed {user}')
            return f'You unfollowed {user.mention} <:catOK:993819099023036456>'
        else:
            return "You're not following anyone yet. You could though, using </follow:1015342375360540753>"

    def getfollowers(self, userid):
        data = collection.find_one({ '_id': userid }, { 'follower_count': 1, '_id': 0 })
        if data is None or data == {}:
            return 0
        else:
            return data['follower_count']

    async def slashfollow(self, user, interactionid):
        if user.id == interactionid:
            return "Nice try, but you can't follow yourself, nerd. <a:wiggleCRAZY:1008697272474816583>"
        self.checkForUser(interactionid)
        if not self.checkopt(user.id):
            return f"{user.mention} isn't accepting followers at the moment."
        res = self.updateDB(interactionid, {'$addToSet': {'following': user.id}})
        if res.modified_count == 0 and res.upserted_id is None:
            return "You're already following this user. <:catOK:993819099023036456>"
        self.updateDB(user.id, {'$inc': {'follower_count': 1}})
        return int(user.id)

    def checkopt(self, userid):
        data = self.getData({ '_id': userid })
        if data is None:
            return False
        elif data['opt'] == 'Enabled':
            return True
        else:
            return False

    def getData(self, query):
        return collection.find_one(query)

    def checkForUser(self, userid):
        query = { '_id': userid }
        if collection.count_documents(query) == 0:
            self.insertDB(userid)
            return True
        else:
            return True

    def insertDB(self, userid):
        query = { '_id': userid, 'opt': 'Enabled', 'channels': [], 'follower_count': 0, 'following': [], 'mute_dm': '',
                  'image_count': 0 }
        collection.insert_one(query)

    def updateDB(self, userid, data):
        query = { '_id': userid }
        return collection.update_one(query, data, upsert=True)

def setup(bot):
    bot.add_cog(FollowerBot(bot))