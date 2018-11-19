import os
import asyncio
import psycopg2
import datetime
import copy
from urllib.parse import urlparse
import select

"""
## SCHEMA ##
CREATE TABLE reminders(
 id serial PRIMARY KEY,
 user_id VARCHAR (50) NOT NULL,
 reminder VARCHAR (255) NOT NULL,
 reminder_date TIMESTAMP NOT NULL,
 created_on TIMESTAMP NOT NULL
);
"""

def connect():
  url = urlparse(os.environ['DATABASE_URL'])
  dbname = url.path[1:]
  user = url.username
  password = url.password
  host = url.hostname
  port = url.port
  conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port,
    sslmode='require')
  return conn

def insert_reminder(user, reminder, reminder_date):
  conn = connect()
  cur = conn.cursor()
  cur.execute('INSERT INTO reminders(user_id, reminder, reminder_date, created_on) VALUES(%s, %s, %s, %s);', (user.id, reminder, reminder_date, datetime.datetime.now()))
  conn.commit()
  cur.close()
  conn.close()

def most_recent_reminder():
  conn = connect()
  cur = conn.cursor()
  cur.execute('SELECT * FROM reminders ORDER BY reminder_date ASC LIMIT 1;')
  result = copy.copy(cur.fetchone())
  cur.close()
  conn.close()
  return result

def list_reminders():
  conn = connect()
  cur = conn.cursor()
  cur.execute('SELECT * FROM reminders ORDER BY reminder_date ASC;')
  results = copy.copy(cur.fetchall())
  cur.close()
  conn.close()
  return results

def delete_all_reminders():
  conn = connect()
  cur = conn.cursor()
  cur.execute('DELETE FROM reminders;')
  conn.commit()
  cur.close()
  conn.close()

def delete_reminder_by_row(n):
  conn = connect()
  cur = conn.cursor()
  cur.execute(f'SELECT * FROM reminders ORDER BY reminder_date ASC LIMIT 1 OFFSET {n};')
  result = copy.copy(cur.fetchone())
  cur.execute(f'DELETE FROM reminders WHERE id = {result[0]};')
  conn.commit()
  cur.close()
  conn.close()
  return result[2]

def delete_reminder_by_id(id):
  conn = connect()
  cur = conn.cursor()
  cur.execute(f'DELETE FROM reminders WHERE id = {id} RETURNING *;')
  result = copy.copy(cur.fetchone())
  conn.commit()
  cur.close()
  conn.close()
  return result