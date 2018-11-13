import discord
import asyncio
import dateparser
import datetime
import pickle
import re
import copy

client = None
keys = 'keys.data'
storage = 'storage.data'

async def secretary(bot, message):
  global client

  client = bot
  
  await command(message)

async def command(message):
  global keys, storage

  if message.content.startswith('!remindme'):
    res = re.search('!remindme (.*) (on|at|in) (.*)', message.content)
    try:
      reminder = res.group(1)
      time = f'{res.group(2)} {res.group(3)}'
      date = dateparser.parse(time, settings={'PREFER_DATES_FROM': 'future'})

      # Read data from file
      reminders = await read_data(storage)
      dates = await read_data(keys)

      key = (date, datetime.datetime.now())
      reminders[key] = (message.author, reminder)
      dates.append(key)
      dates = sorted(dates, key=lambda x: x[0])

      # Save data
      await save_data(storage, reminders)
      await save_data(keys, dates)

      await client.send_message(message.channel, f':pen_fountain: I will remind you to `{reminder}` on {key[0].strftime("%d/%m/%y at %I:%M%p")}.')
    except:
      await error(message.channel)
  elif message.content.startswith('!purge'):
    await save_data(storage, {})
    await save_data(keys, [])

    await client.send_message(message.channel, ':pen_fountain: All reminders cleared.')
  elif message.content.startswith('!list'):
    embed = discord.Embed(title=f'Reminders', color=0x888888)

    reminders = await read_data(storage)
    dates = await read_data(keys)

    for index, key in enumerate(dates):
      embed.add_field(name=f'{index + 1}. {reminders[key][1]}', value=f'{key[0].strftime("%d/%m/%y - %I:%M%p")}', inline=False)

    await client.send_message(message.channel, embed=embed)
  elif message.content.startswith('!remove '):
    try:
      index = int(message.content.split()[1]) - 1

      reminders = await read_data(storage)
      dates = await read_data(keys)

      key = dates[index]
      reminder = copy.copy(reminders[key][1])
      dates.remove(key)
      del reminders[key]

      await save_data(storage, reminders)
      await save_data(keys, dates)

      await client.send_message(message.channel, f':pen_fountain: I will no longer remind you to `{reminder}`.')
    except:
      await error(message.channel)
  elif message.content.startswith('!help'):
    embed = discord.Embed(title=f'Commands', color=0x888888, description="""

    `!remindme [reminder] (on|at|in) [time]`

    `!list`

    `!remove [#]`

    `!purge`

    `!help`
    """)

    await client.send_message(message.channel, embed=embed)
  else:
    await client.send_message(message.channel, "Use `!help` for more info.")

async def check_reminders():
  while True:
    global keys, storage
    reminders = await read_data(storage)
    dates = await read_data(keys)

    if len(dates) > 0:
      key = dates[0]
      try:
        if key[0] <= datetime.datetime.now():
          author = reminders[key][0]
          reminder = reminders[key][1]
          reminder_copy = copy.copy(reminder)

          await client.send_message(author, f'Reminder: {reminder_copy}')

          dates.remove(key)
          del reminders[key]

          await save_data(storage, reminders)
          await save_data(keys, dates)
      except:
        continue
    await asyncio.sleep(1)

async def read_data(file):
  f = open(file, 'rb')
  data = pickle.load(f)
  return data

async def save_data(file, data):
  f = open(file, 'wb')
  pickle.dump(data, f)
  f.close()

async def error(channel):
  await client.send_message(channel, 'That was not a valid command. Please use `!help` for more info.')