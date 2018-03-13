### IMPORTS ###
from __future__ import division
import csv
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime, time

## GLOBAL VARIABLES ###


## FUNCTIONS ###


# Fetches csv-file from Keparoi-nimenhuuto
def fetch_calendar_csv():
    url = 'https://keparoi.nimenhuuto.com/calendar/csv'
    response = urllib2.urlopen(url)
    return csv.reader(response)


# Fetches html for specific event and finds player names
def fetch_event_parse_names(url):
    names = []
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, "lxml")
    for span in soup.select("#zone_3 > span"):
        names.append("".join(span.text.split()))
    return names


# Sends timetable for next week
def send_timetable():
    print("NOT WORKING")


# Reminds to update IN/OUTS-status for specific training
def send_reminder():
    print("NOT WORKING")


# Sends Messenger-message with Facebook Messenger API
def send_chat_message():
    print("NOT WORKING")


# Find hours between dates
def delta_hours(date):
    delta = datetime.strptime(date, "%Y-%m-%dT%H:%M")- datetime.now()
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Returns (total hours , minutes)
    return days*24 + hours, minutes


def main():
    event_list = fetch_calendar_csv()
    time_now = datetime.now().time()
    weekday = datetime.today().weekday()

    # Check if sunday evening for sending schedule
    if weekday == 6 and time(21, 0) <= time_now <= time(21, 30):
        print("NOT WORKING")

    iter_events = iter(event_list)
    next(iter_events)

    for row in iter_events:
        date = row[1]
        starting_time = row[2]
        event_url = "".join(row[4].split(" ")[0])
        date_iso= date + "T" + starting_time
        hours, minutes = delta_hours(date_iso)
        print(fetch_event_parse_names(event_url))
        if hours == 12 or hours == 24 or hours == 48:
            if minutes < 30:
                print("NOT WORKING")


if __name__ == "__main__":
    main()