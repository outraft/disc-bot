from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
import os # env
import discord # zaten
from pymongo import MongoClient # mongodb
from datetime import datetime, timezone, timedelta # zamanlama
from uuid import uuid4
import pytz

load_dotenv()

# Mongo DB stuff
client = MongoClient(os.getenv("LOCAL_MONGO_CLIENT"))
db = client["bottest"]
collection = db["testcollection"]
timedevents = db["timedevents"]
settings = db["settings"]

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
		embed.add_field(name="/testargs", value="Test how the args work with the help from the code!", inline=True)
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

	@app_commands.command(name="testargs", description="Test command /w args")
	# Adding arguments to the command - Example
	async def test_args(self, interaction: discord.Interaction, arg1: str, arg2: str):
		await interaction.response.send_message(f"Received arguments: {arg1} and {arg2}", ephemeral=True)

	@app_commands.command(name="testdb-send", description="Sends a message to the database!")
	async def testdb_send(self, interaction: discord.Interaction, arg1: str):
		user_uuid = str(uuid4())
		# * User mesajı dbye
		collection.insert_one({"uuid": user_uuid, "message": arg1, "userID": interaction.user.id, "timestamp": datetime.now(tz=timezone.utc)})

		await interaction.response.send_message(f"Sent \"{arg1}\" to the database with ID: \"{user_uuid}\"!", ephemeral=True)

	@app_commands.command(name="testdb-pull-id", description="Pull the message sent from the database with respect to the messageid!")
	async def testdb_pull(self, interaction: discord.Interaction, id: str):
		try:
			messagefound = collection.find_one({"uuid": id})
			if not messagefound:
				raise ValueError("No Document found")
			id = messagefound.get("userID", "No user found")
			message = messagefound.get("message")
			await interaction.response.send_message(f"Pulled message from {await self.bot.fetch_user(id)}: \"{message}\"")
		except Exception as e:
			await interaction.response.send_message(f"No message with id \'{id}\' was found! Are you sure that it was sent?")

	@app_commands.command(name="testdb-pullall", description="Pulls last 5 messages with ID's associated!")
	async def testdb_pullall(self, interaction: discord.Interaction, user: discord.User = None):
		if user is None:
			user = interaction.user
		username = user.name
		id = user.id
		user_pfp = user.display_avatar.url

		embed = discord.Embed()
		embed.title = f"{username}'s last 5 messages:"
		embed.set_thumbnail(url=user_pfp)
		results = collection.find({"userID": id}).sort("timestamp", -1).limit(5)

		for i, doc in enumerate(results, 1):
			content = doc.get("message", "*No message.*")
			timestamp = doc.get("timestamp", "*Unknown time.*")
			msg_id = doc.get("uuid", "*No UUID found.*")
			embed.add_field(
				name=f"#{i} \n• ID: {msg_id}",
				value=f"Message sent: {content}\n Timestampt @: {timestamp}",
				inline= False
			)
		await interaction.response.send_message(embed=embed, ephemeral=True)
	@app_commands.command(name="timed-message", description="Times the message to a date after x hours")
	async def timed_message(self, interaction: discord.Interaction, date: str, eventname: str, isembed: bool):
		try:
			# Kullanıcının girdiği string saati datetime'a çevir
			date = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
			# Şu anki zamanı da düzgün al
			now = datetime.now()

		except ValueError:
			await interaction.response.send_message("Wrong date format! Use: `DD-MM-YYYY HH:MM:SS`", ephemeral=True)
			return

		delta = (date - now).total_seconds()
		if delta <= 0:
			await interaction.response.send_message("The time difference can not be negative!", ephemeral=True)
			return

		# Mongo UTC sever
		trigger_utc = date.astimezone(pytz.utc)
		now_utc = now.astimezone(pytz.utc)

		event_id = uuid4().hex
		timedevents.insert_one({
			"uuid": event_id,
			"eventname": eventname,
			"isEmbed": isembed,
			"channel": interaction.channel_id,
			"trigger_at": trigger_utc,
			"created_at": now_utc
		})

		await interaction.response.send_message(
			f"The timer for {eventname} is set for {date.strftime('%d-%m-%Y %H:%M:%S')} (TR time). "
			f"It {'will' if isembed else 'will not'} be in embed format. Event ID: {event_id}"
		)
	@app_commands.command(name="addsetting", description="Adds a setting to your embed parses!")
	async def addsetting(self, interaction: discord.Interaction, settingName: str, title: str = None, thn: str = None, fieldName: str = None, value: str = None, desc: str = None, color: str = None):
		setting_id = uuid4().hex
		settings.insert_one{

		}


#TODO ADD A TIMED COMMAND
#TODO2 DO A WEBSCRAPER PROJECT FOR WHO KNOWS WHY
#NOTE LEARN THE DAMN ROBOTS.TXT FOR WEBSCRAPING