### IMPORTS ###

import logging
import csv
import sys
from io import StringIO
from urllib.request import urlopen
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, time
from fbchat import Client
from fbchat.models import *

import os

### FUNCTIONS ###


# Send test message
def send_test_message():
    send_chat_message("Testing functionality, ignore this message")

# Gets session token from file
def get_session_token():
    session_token = ''
    token_path = os.path.join(bot_path, "session_token.txt")
    try:
        f = open(token_path, "r")
        session_token += f.read()
        f.close()
    except:
        logservice.error("Could not read session token from the file")
    print(session_token)
    return session_token

# Writes session token to a file (overwrites the old one)
def set_session_token(token):
    token_path = os.path.join(bot_path, "session_token.txt")
    try:
        f = open(token_path, "w+")
        f.write(str(token))
        f.seek(0)
        f.close()
    except:
        logservice.error("Could not write session token to a file")


# Fetches csv-file from Keparoi-nimenhuuto
def fetch_calendar_csv():
    url = 'https://keparoi.nimenhuuto.com/calendar/csv'
    df = pd.read_csv(url)
    buffer = StringIO()
    df.to_csv(buffer)
    buffer.seek(0)
    return csv.reader(buffer)


# Fetches html for specific event and finds player names
def fetch_event_parse_names(url):
    names = []
    page = urlopen(url)
    soup = BeautifulSoup(page, "lxml")
    for span in soup.select("#zone_3 > span"):
        names.append("".join(span.text.split()))
    return names


# Sends timetable for next week
def send_timetable(happenings):
    message = "Next week schedule: \n"
    message = message + "\n".join(happenings)
    send_chat_message(message)


# Reminds to update IN/OUTS-status for specific training
def send_reminder(names, event_url, recap, date_str):
    names = " ".join(names)
    if names != "Eiketään":
        message = "MUISTUTUS:\nIN / OUT\n{} {}\n({})\n{}\n".format(date_str,recap, event_url, names)
        send_chat_message(message)

# Sends Messenger-message with Facebook Messenger API
def send_chat_message(message):
    client = Client('<email>', '<password>', session_cookies=get_session_token())
    set_session_token(client.getSession())
    client.send(Message(text=message), thread_id='500949883413912',
                thread_type=ThreadType.GROUP)
    logservice.info("MESSAGE SENT")


# Find hours between dates
def delta_hours(date):
    delta = datetime.strptime(date, "%Y-%m-%dT%H:%M") - datetime.now()
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Returns (total hours , minutes)
    return days*24 + hours, minutes


### MAIN ###

def main():
    weekdays = ['MAANANTAINA','TIISTAINA','KESKIVIIKKONA','TORSTAINA','PERJANTAINA','LAUANTAINA','SUNNUNTAINA']

    global logservice
    logservice = logging.getLogger()
    logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logservice.addHandler(ch)

    logservice.info("STARTING KEPAROI BOT")

    global bot_path
    global bot_email
    global bot_pwd

    try:
        bot_path = os.environ['keparoibotPath']
    except KeyError:
        logservice.critical(
            "Please set the environment variable keparoibotPath")
        sys.exit(1)

    try:
        bot_email = os.environ['keparoibotEmail']
    except KeyError:
        logservice.critical(
            "Please set the environment variable keparoibotEmail")
        sys.exit(1)

    try:
        bot_pwd = os.environ['keparoibotPw']
    except KeyError:
        logservice.critical("Please set the environment variable keparoibotPw")
        sys.exit(1)

    event_list = fetch_calendar_csv()
    time_now = datetime.now().time()
    weekday = datetime.today().weekday()

    iter_events = iter(event_list)
    next(iter_events)

    happenings = []

    for row in iter_events:
        recap = row[1]
        date = row[2]
        starting_time = row[3]
        event_url = "".join(row[5].split(" ")[0])
        date_iso = date + "T" + starting_time
        weekday_number = datetime.strptime(date_iso, "%Y-%m-%dT%H:%M").weekday()
        hours, minutes = delta_hours(date_iso)
        names = fetch_event_parse_names(event_url)
        if hours < 171 and hours > 3:
            happenings.append("{}\n {} \n ({})\n".format(
                weekdays[weekday_number], recap, event_url))

        if hours == 12 or hours == 30 or hours == 48:
            if minutes < 30:
                send_reminder(names, event_url, recap, weekdays[weekday_number])

    if len(happenings) > 0 and weekday == 6 and time(21, 0) <= time_now <= time(21, 30):
        send_timetable(happenings)

    logservice.info("STOPPING KEPAROI BOT")

if __name__ == "__main__":
    main()
