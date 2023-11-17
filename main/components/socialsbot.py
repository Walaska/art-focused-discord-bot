import os
import nextcord
import requests
import validators
from nextcord.ext import commands
from pymongo import MongoClient
from urllib import parse

db_url = f"mongodb+srv://neyasbot:rtv7uxHIwWkiIiwb@digitalart.k4xqkao.mongodb.net/?retryWrites=true&w=majority"
cluster = MongoClient(db_url)
db = cluster["socialsbot"]
collection = db["socials"]

class SocialsBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def socialsBotAllowedChannels(self, channel_id):
        return True if channel_id in [903596413231964191, 903596378293411891, 903596456466853969, 903596435663097907, 1143976152348770434] else False

    @commands.Cog.listener()
    async def on_ready(self):
        print('SocialsBot working...')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.attachments != [] and self.socialsBotAllowedChannels(message.channel.id):
            res = await self.messageTypeImage(message)

    @nextcord.slash_command(description="Remove socials from your list", guild_ids=[903586180711481385])
    async def disconnect(
            self,
            interaction: nextcord.Interaction,
            media: str = nextcord.SlashOption(
                name="platform",
                choices={'instagram': 'instagram', 'twitter': 'twitter', 'deviantart': 'deviantart', 'tumblr': 'tumblr',
                         'artstation': 'artstation', 'pixiv': 'pixiv'},
            ),
    ):
        if self.removeURL(interaction.user.id, media) == 100:
            await interaction.response.send_message('No link added for this platform yet.')
        else:
            await interaction.response.send_message('Profile removed successfully!')

    @nextcord.slash_command(description="Show all your socials!", guild_ids=[903586180711481385])
    async def list(
            self,
            interaction: nextcord.Interaction,
    ):
        if await self.displayEmbed(interaction.user, interaction.response.send_message) == 100:
            await interaction.response.send_message("You didn't add any socials yet, use </connect:1002694507688640552> to get started")

    @nextcord.slash_command(description="Register your social media profiles", guild_ids=[903586180711481385])
    async def connect(
            self,
            interaction: nextcord.Interaction,
            instagram: str = nextcord.SlashOption(
                name="instagram",
                description="Enter @username or full profile URL",
                required=False
            ),
            twitter: str = nextcord.SlashOption(
                name="twitter",
                description="Enter @username or full profile URL",
                required=False
            ),
            deviantart: str = nextcord.SlashOption(
                name="deviantart",
                description="Enter username or full profile URL",
                required=False
            ),
            tumblr: str = nextcord.SlashOption(
                name="tumblr",
                description="Enter username or blog URL",
                required=False
            ),
            artstation: str = nextcord.SlashOption(
                name="artstation",
                description="Enter username or full profile URL",
                required=False
            ),
            pixiv: str = nextcord.SlashOption(
                name="pixiv",
                description="Enter user # or full profile URL",
                required=False
            )
    ):
        registered = []
        register_error = []
        option_value = 0
        if instagram is not None:
            ig_url = self.checkURL(interaction.data["options"][option_value]["value"], 'instagram')
            if ig_url == 'failed':
                register_error.append('instagram')
            else:
                self.insertToDb(interaction.user.id, 'instagram', ig_url)
                registered.append('instagram')
                option_value += 1
        if twitter is not None:
            tw_url = self.checkURL(interaction.data["options"][option_value]["value"], 'twitter')
            if tw_url != 'failed':
                self.insertToDb(interaction.user.id, 'twitter', tw_url)
                registered.append('twitter')
                option_value += 1
            else:
                register_error.append('twitter')
        if deviantart is not None:
            da_url = self.checkURL(interaction.data["options"][option_value]["value"], 'deviantart')
            if da_url != 'failed':
                self.insertToDb(interaction.user.id, 'deviantart', da_url)
                registered.append('deviantart')
                option_value += 1
            else:
                register_error.append('deviantart')
        if tumblr is not None:
            tb_url = self.checkURL(interaction.data["options"][option_value]["value"], 'tumblr')
            if tb_url != 'failed':
                self.insertToDb(interaction.user.id, 'tumblr', tb_url)
                registered.append('tumblr')
                option_value += 1
            else:
                register_error.append('tumblr')
        if artstation is not None:
            ar_url = self.checkURL(interaction.data["options"][option_value]["value"], 'artstation')
            if ar_url != 'failed':
                self.insertToDb(interaction.user.id, 'artstation', ar_url)
                registered.append('artstation')
                option_value += 1
            else:
                register_error.append('artstation')
        if pixiv is not None:
            px_url = self.checkURL(interaction.data["options"][option_value]["value"], 'pixiv')
            if px_url != 'failed':
                self.insertToDb(interaction.user.id, 'pixiv', px_url)
                registered.append('pixiv')
                option_value += 1
            else:
                register_error.append('pixiv')
        response_msg = ""
        if len(registered) != 0:
            response_msg = "Successfully added: \n"
            for platform in registered:
                response_msg += platform + ','
            response_msg = response_msg.removesuffix(',')
        if len(register_error):
            response_msg += "\nSomething went wrong with these: \n"
            for e in register_error:
                response_msg += e + ','
            response_msg = response_msg.removesuffix(',')
        await interaction.response.send_message(response_msg)

    async def messageTypeImage(self, message):
        x = 0
        pic_types = ['.png', '.jpg', '.jpeg']
        for attachment in message.attachments:
            for extension in pic_types:
                if attachment.filename.endswith(extension):
                    if self.getuser(message.author.id) == 0:
                        return
                    x += 1
        if x > 0:
        	await self.displayEmbed(message.author, message.channel.send)

    async def displayEmbed(self, author, message):
        urls = self.getUrls(author.id)
        fbot = self.bot.get_cog('FollowerBot')
        followers = fbot.getfollowers(author.id)
        if self.getuser(author.id) == 0:
            return 100
        ig_d, tw_d, da_d, tb_d, ar_d, px_d = "x", "x", "x", "x", "x", "x"
        for x in urls:
            ig_d = x['ig']
            tw_d = x['tw']
            da_d = x['da']
            tb_d = x['tb']
            ar_d = x['ar']
            px_d = x['px']
        count = 0
        embed = nextcord.Embed(title="", description="", color=nextcord.Color.from_rgb(54, 57, 63))
        embed.set_thumbnail(url=author.avatar.url)
        if ig_d != "":
            embed.add_field(name="<:ig:1012713053231534130>  Instagram", value=f"[Click here]({ig_d})", inline=True)
            count += 1
        if tw_d != "":
            embed.add_field(name="<:twitter:1012713043785941043>  Twitter", value=f"[Click here]({tw_d})", inline=True)
            count += 1
        if da_d != "":
            embed.add_field(name="<:deviantart:1012713055261569105>  DeviantArt", value=f"[Click here]({da_d})",
                            inline=True)
            count += 1
        if tb_d != "":
            embed.add_field(name="<:tumblr:1012713046810034236>  Tumblr", value=f"[Click here]({tb_d})", inline=True)
            count += 1
        if ar_d != "":
            embed.add_field(name="<:artstation:1012713057643933726>  ArtStation", value=f"[Click here]({ar_d})",
                            inline=True)
            count += 1
        if px_d != "":
            embed.add_field(name="<:pixiv:1012713050454884352>  Pixiv", value=f"[Click here]({px_d})", inline=True)
            count += 1
        if count == 5:
            embed.add_field(name='\u200B', value='\u200B', inline=True)
        if count == 0:
            return 100
        embed.set_footer(text=f'Social Media links for {author} \n' + f'Followers: {followers} \n' + 'Add yours using /connect')
        # await message.channel.send('\u200B')
        await message(embed=embed)

    def getQueryString(self, id, pf, url):
        if pf == 'instagram':
            return { "_id": id, "ig": url, "tw": "", "da": "", "tb": "", "ar": "", "px": "" }
        elif pf == 'twitter':
            return { "_id": id, "ig": "", "tw": url, "da": "", "tb": "", "ar": "", "px": "" }
        elif pf == 'deviantart':
            return { "_id": id, "ig": "", "tw": "", "da": url, "tb": "", "ar": "", "px": "" }
        elif pf == 'tumblr':
            return { "_id": id, "ig": "", "tw": "", "da": "", "tb": url, "ar": "", "px": "" }
        elif pf == 'artstation':
            return { "_id": id, "ig": "", "tw": "", "da": "", "tb": "", "ar": url, "px": "" }
        elif pf == 'pixiv':
            return { "_id": id, "ig": "", "tw": "", "da": "", "tb": "", "ar": "", "px": url }

    def insertToDb(self, id, pf, url):
        query = { "_id": id }
        if collection.count_documents(query) == 0:
            query = self.getQueryString(id, pf, url)
            collection.insert_one(query)
        else:
            query = { "_id": id }
            userinfo = collection.find(query)
            if pf == 'instagram':
                collection.update_one({"_id": id}, {"$set":{"ig": url}})
            elif pf == 'twitter':
                collection.update_one({"_id": id}, {"$set":{"tw": url}})
            elif pf == 'deviantart':
                collection.update_one({"_id": id}, {"$set":{"da": url}})
            elif pf == 'tumblr':
                collection.update_one({"_id": id}, {"$set":{"tb": url}})
            elif pf == 'artstation':
                collection.update_one({"_id": id}, {"$set":{"ar": url}})
            elif pf == 'pixiv':
                collection.update_one({"_id": id}, {"$set":{"px": url}})

    def is_string_an_url(self, url_string: str, pf) -> bool:
        result = validators.url(url_string)

        split = parse.urlsplit(url_string)
        netloc = split.netloc
        path = split.path
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        print(netloc + path.rstrip('/'))
        neturl = netloc + path.rstrip('/')
        naked_url = neturl.split('.', 1)[0]
        naked_url = naked_url.split('/',1)[0]
        if isinstance(result, ValidationFailure):
            return False
        if naked_url != pf and pf != "img":
            return False
        return True

    def removeURL(self, id, pf):
        ig_d, tw_d, da_d, tb_d, ar_d, px_d = "", "", "", "", "", ""
        query = { "_id": id }
        userinfo = collection.find(query)
        for dtype in userinfo:
            ig_d = dtype['ig']
            tw_d = dtype['tw']
            da_d = dtype['da']
            tb_d = dtype['tb']
            ar_d = dtype['ar']
            px_d = dtype['px']
        if pf == 'instagram':
            collection.update_one({"_id": id}, {"$set": {"ig": ""}})
            if ig_d == "":
                return 100
        elif pf == 'twitter':
            collection.update_one({"_id": id}, {"$set": {"tw": ""}})
            if tw_d == "":
                return 100
        elif pf == 'deviantart':
            collection.update_one({"_id": id}, {"$set": {"da": ""}})
            if da_d == "":
                return 100
        elif pf == 'tumblr':
            collection.update_one({"_id": id}, {"$set": {"tb": ""}})
            if tb_d == "":
                return 100
        elif pf == 'artstation':
            collection.update_one({"_id": id}, {"$set": {"ar": ""}})
            if ar_d == "":
                return 100
        elif pf == 'pixiv':
            collection.update_one({"_id": id}, {"$set": {"px": ""}})
            if px_d == "":
                return 100

    def checkURL(self, url_object, pf):
        print(url_object)
        urlstr = str(url_object)
        if '@' in urlstr:
            url = urlstr.replace("@", "")
        else:
            url = url_object
        print(url)
        if url.startswith('https://'):
            if self.is_string_an_url(url, pf):
                return url
            else:
                return 'failed'
        elif url.startswith('http://'):
            newurl = url.replace('http', 'https')
            if self.is_string_an_url(newurl, pf):
                return newurl
            else:
                return 'failed'
        elif url.startswith('www.'):
            if self.is_string_an_url('https://' + url, pf):
                return 'https://' + url
            else:
                return 'failed'
        elif url.startswith(pf):
            if self.is_string_an_url('https://wwww.' + url, pf):
                return 'https://wwww.' + url
            else:
                return 'failed'
        else:
            if pf == 'pixiv':
                if self.is_string_an_url('https://www.pixiv.net/en/users/' + url, pf):
                    return 'https://www.pixiv.net/en/users/' + url
                else:
                    return 'failed'
            elif pf == 'tumblr':
                if self.is_string_an_url('https://www.tumblr.com/blog/' + url, pf):
                    return 'https://www.tumblr.com/blog/' + url
                else:
                    return 'failed'
            else:
                if self.is_string_an_url('https://www.' + pf + '.com/' + url, pf):
                    return 'https://www.' + pf + '.com/' + url
                else:
                    return 'failed'

    def is_url_image(self, image_url):
       image_formats = ("image/png", "image/jpeg", "image/jpg")
       r = requests.head(image_url)
       print("test-test-test: ", r.headers["content-type"])
       if r.headers["content-type"] in image_formats:
          return True
       return False

    def getuser(self, id):
        query = { '_id': id }
        user = collection.find(query)
        userlist = list(user)
        return len(userlist)
    
    def getUrls(self, id):
        query = { '_id': id }
        userinfo = collection.find(query)
        return userinfo

def setup(bot):
    bot.add_cog(SocialsBot(bot))