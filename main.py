from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import os
from bot_commands import BotCommands
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient # mongodb
from datetime import datetime
import pytz
import settings_parser as sp

client = AsyncIOMotorClient(os.getenv("LOCAL_MONGO_CLIENT"))
db = client["bottest"]
timedevents = db["timedevents"]
load_dotenv()

TEST_GUILD_ID = int(os.getenv("TEST_GUILD_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

async def setup_hook():
	await bot.add_cog(BotCommands(bot))

@bot.event
async def on_ready():
    testguildsync = await bot.tree.sync(guild=discord.Object(id=TEST_GUILD_ID))
    print(f"{len(testguildsync)} tane guild komut(lar)ı sync edildi.")

    sync = await bot.tree.sync()
    print(f"{len(sync)} tane global komut(lar)ı sync edildi.")

    print(f"{bot.user} olarak giriş yapıldı!")
    asyncio.tasks.create_task(timed_message_dispatcher())

async def timed_message_dispatcher():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.now(pytz.utc)
        due_events = timedevents.find({"trigger_at": {"$lte": now}})

        async for event in due_events:
            channel = await bot.fetch_channel(event['channel'])
            message = f"The event {event['eventname']} is happening now!"

            if event['isEmbed']:
                embed = discord.Embed(title= f"The event {event['eventname']} is happening now!")
                await channel.send(embed=embed)
            else:
                await channel.send(message)

            timedevents.delete_one({"_id": event["_id"]})
        await asyncio.sleep(15)

bot.setup_hook = setup_hook
bot.run(os.getenv("TOKEN"))
