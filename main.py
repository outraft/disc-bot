from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
from bot_commands import BotCommands

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


bot.setup_hook = setup_hook
bot.run(os.getenv("TOKEN"))
