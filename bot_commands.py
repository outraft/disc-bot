from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
import os
import discord

load_dotenv()

TEST_GUILD_ID = int(os.getenv("TEST_GUILD_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

class BotCommands(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@app_commands.command(name="ping", description="Latency test!")
	async def ping2(self, interaction: discord.Interaction):
		message = "not bad..." if round(self.bot.latency * 1000) < 200 else "could be better..."  if round(self.bot.latency * 1000) < 1000 else "no comment..." # seems complicated but it is just a simple latency check with emotions lol
		await interaction.response.send_message(f"Pong! Latency: {round(self.bot.latency * 1000)}ms, {message}", ephemeral=True)

	@app_commands.command(name="help", description="For any questions you might have!")
	async def help(self, interaction: discord.Interaction):
		embed = discord.Embed(title="Help", description="Here are some commands you can use:", color=discord.Color.blue())
		embed.set_thumbnail(url=self.bot.user.avatar.url)
		embed.add_field(name="/ping", value="Check the bot's latency.", inline=False)
		embed.add_field(name="/help", value="Get help with the bot.", inline=False)
		await interaction.response.send_message(embed=embed, ephemeral=True)

	@app_commands.command(name="motivation", description="Get a random motivational quote!")
	async def motivation(self, interaction: discord.Interaction):
		from motivationalquotes import quotes, titles
		import datetime
		import random

		seed = datetime.datetime.today().strftime("%Y%m%d")
		random.seed(seed)
		# Embedisation of the quote
		embed = discord.Embed(title=random.choice(titles), color=discord.Color.blue())
		embed.set_thumbnail(url=self.bot.user.avatar.url)
		embed.add_field(name= "Mo Paz quote of the day: ", value=random.choice(quotes), inline=False)

		await interaction.response.send_message(embed=embed, ephemeral=True)