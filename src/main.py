import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('DISCORD_PREFIX')

# Define intents
intents = discord.Intents.default()
intents.message_content = True

# Create a bot instance with a command prefix
if not PREFIX:
    command_prefix="!"
else:
    command_prefix=PREFIX

bot = commands.Bot(command_prefix=command_prefix, intents=intents)

# Event listener for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.tree.sync()
    print("Slash commands synced.")
    print('------')

# Asynchronous function to load cogs
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

# Main function to run the bot
async def main():
    await load_cogs()
    await bot.start(TOKEN)

# Run the bot
if __name__ == '__main__':
    asyncio.run(main())
