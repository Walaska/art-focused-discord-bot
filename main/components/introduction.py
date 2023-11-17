import os
import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta
from pymongo import MongoClient

db_url = f"mongodb+srv://neyasbot:rtv7uxHIwWkiIiwb@digitalart.k4xqkao.mongodb.net/?retryWrites=true&w=majority"
cluster = MongoClient(db_url)
db = cluster["utilities"]
collection = db["misc"]

class Introduction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.toBeRemoved = []
        self.checkIntros()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Introduction bot online...')
        guild = self.bot.get_guild(903586180711481385)
        role = nextcord.utils.get(guild.roles, name='Introduced')
        if len(self.toBeRemoved) > 0:
            for x in self.toBeRemoved:
                user = guild.get_member(x)
                try:
                	await user.remove_roles(role)
                except:
                    pass
    
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.thread is not None:
            if msg.thread.parent_id == 1020272530356981801 and self.checkIfNew(msg.author.id):
                role = nextcord.utils.get(msg.guild.roles, name='Introduced')
                await msg.author.add_roles(role)

    def checkIntros(self):
        date = datetime.today()
        seven_days_ago = date - timedelta(days=7)
        x = collection.find({ 'introduced_date': { '$lt': seven_days_ago} })
        for y in x:
            self.toBeRemoved.append(y['_id'])
        collection.delete_many( { 'introduced_date': { '$lt': seven_days_ago} } )

    def checkIfNew(self, userid):
        query = { '_id': userid }
        if collection.count_documents(query) == 0:
            self.insertDB(userid)
            return True
        else:
            return True

    def insertDB(self, userid):
        date = datetime.today()
        query = { '_id': userid, 'introduced_date': date }
        collection.insert_one(query)

def setup(bot):
    bot.add_cog(Introduction(bot))