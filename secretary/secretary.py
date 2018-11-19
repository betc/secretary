import discord
import asyncio
import dateparser
import datetime
import pickle
import re
import copy
import psycopg2
import db

client = None

async def secretary(bot, message):
  global client

  client = bot
  
  await command(message)

async def command(message):
  if message.content.startswith('!remindme'):
    res = re.search('!remindme (.*) (on|at|in) (.*)', message.content)
    try:
      reminder = res.group(1)
      time = f'{res.group(2)} {res.group(3)}'
      date = dateparser.parse(time, settings={'PREFER_DATES_FROM': 'future'})

      db.insert_reminder(message.author, reminder, date)
      await client.send_message(message.channel, f':pen_fountain: I will remind you to `{reminder}` on {date.strftime("%d/%m/%y at %I:%M%p")}.')

    except Exception as e:
      print(f'Error inserting: `{e}`')
      await error(message.channel)
  elif message.content.startswith('!purge'):
    try:
      db.delete_all_reminders()
      await client.send_message(message.channel, ':pen_fountain: All reminders cleared.')
    except:
      await db_error(message.channel)
  elif message.content.startswith('!list'):
    embed = discord.Embed(title=f'Reminders', color=0x888888)

    reminders = db.list_reminders()

    for index, reminder in enumerate(reminders):
      embed.add_field(name=f'{index + 1}. {reminder[2]}', value=f'{reminder[3].strftime("%d/%m/%y - %I:%M%p")}', inline=False)

    await client.send_message(message.channel, embed=embed)
  elif message.content.startswith('!remove '):
    try:
      index = str(int(message.content.split()[1]) - 1)

      reminder = db.delete_reminder_by_row(index)

      await client.send_message(message.channel, f':pen_fountain: I will no longer remind you to `{reminder}`.')
    except Exception as e:
      print(f'Error deleting: `{e}`')
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
  global client

  while True:
    reminder = db.most_recent_reminder()

    if reminder is not None and reminder[3] <= datetime.datetime.now():
      try:
        result = db.delete_reminder_by_id(reminder[0])
        member = discord.utils.get(client.get_all_members(), id=reminder[1])
        await client.send_message(member, f'Reminder: {result[2]}')
      except Exception as e:
        print(f'Error sending reminder: {e}')
        continue
    await asyncio.sleep(1)

async def error(channel):
  await client.send_message(channel, 'Something went wrong or that was not a valid command. Please use `!help` for more info.')

async def db_error(channel):
  await client.send_message(channel, 'Something went wrong when attempting to track your reminder, please try again.')