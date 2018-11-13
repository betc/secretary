import discord
import asyncio
import secretary
import config

client = discord.Client()
server = None
@client.event
async def on_ready():
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')

@client.event
async def on_message(message):
  if message.content.startswith('!'):
    await secretary.secretary(client, message)

client.loop.create_task(secretary.check_reminders())
client.run(config.TOKEN)