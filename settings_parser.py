from pymongo import MongoClient
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import os
from bot_commands import BotCommands
import asyncio

load_dotenv()

"""
the default arguments for settings will be:

settings{
	uuid!!!!
	id
	title
	thumbnail
	field
	value
	desc
	timestamp (opt)
	color (opt)

}
"""



# Mongo DB stuff
client = MongoClient(os.getenv("LOCAL_MONGO_CLIENT"))
db = client["bottest"]
settings = db["settings"]

async def settings_parser():
	for _, setting in enumerate(settings.find(), 1):
		if setting.get('_id'):
			print("")


if __name__ == "__main__":
    asyncio.run(settings_parser())
