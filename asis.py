from __future__ import print_function
import os
import sys
import time
import playsound
import speech_recognition as sr
from gtts import gTTS
import pyttsx3
from datetime import datetime, timezone
from datetime import datetime as dt
import pytz
import subprocess

import datetime
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import cl_face
import final as f

import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv

import bs4 as bs
import urllib.request
import requests
import webbrowser
import ssl
import certifi
from PIL import Image
from time import ctime
import random
import pandas as pd
import matplotlib.pyplot as plt
import user_database as user_db
import mask

#Assistant Specs
ASISSTANT_NAME = "alex"

#Developer Mode
DEV_CODE=0000
# Assistant triggers
AWAKE = False
QUIT = "quit"
WAKE = "alex"
SLEEP = "bye alex"
CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
NOTE_STRS = ["make a note", "write this down", "remember this", "type this"]
TRANSL_STRS = ["translate", "translation", "sign language"]
GREETINGS = ['hey','hi','hello']
ASK_ASIS_NAME = ["what is your name","what's your name","tell me your name"]
ASK_TIME = ["what's the time","tell me the time","what time is it","what is the time"]
SEARCH_GOOGLE = ["search for"]
SEARCH_GOOGLE_1 = ["search"]
SEARCH_YOUTUBE = ["youtube"]
WEATHER = ["what is the weather", "tell me the weather"]
ASK_MY_LOCATION = ["where am i"]
ASK_MY_EXACT_LOCATION = ["what is my exact location"]
WIKIPEDIA = ["definition of"]

#COVID-19
COVID_MSG = ["covid sms permission", "send message for permission", "send covid sms"]
COVID_STATS = ["covid news", "covid stats", "covid cases"]



###Defining Months and Days###
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]


# Func-> Assistant speaks
def covid_codes_help():
    print("1 to go to a pharmacy or attending an appointment with a doctor")
    print("2 to go to the supermarket if it is not possible for groceries to be delivered")
    print("3 to go to a public service office with a scheduled appointment and to the bank")
    print("4 to provide assistance to people in need or to accompany young students (minors) to/from school")
    print("5 to go to a funeral under the conditions provided by law or if divorced/separated parents need to go outdoors for reasons concerning their child/children")
    print("6 to exercise outdoors (jogging) or walk a pet, solitary or strictly in pairs and observing the necessary distance of 1.5 meters from one another")


def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty("rate", 140)
    engine.say(text)
    engine.runAndWait()


# Func-> User speaks
def get_audio():
    print("speak")
    r = sr.Recognizer()
    # rec()
    # with sr.AudioFile("1.wav") as source:
    with sr.Microphone() as source:
        #r.pause_threshold=1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print(f"ERROR: {str(e)}")
    return said


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print("No upcoming events found.")
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12)
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)


def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    # If the month mentioned is before the current month set the year to the next
    if month < today.month and month != -1:
        year = year+1

    # If we didn't find a month, but we have a day
    if month == -1 and day != -1:  
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # If we only found a data of the week
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1: 
        print(datetime.date(month=month, day=day, year=year))
        return datetime.date(month=month, day=day, year=year)

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)

    subprocess.Popen(["subl", file_name])

def wearing_mask():
    mask_detection = mask.Mask_Detection()
    can_leave = mask_detection.check()
    speak("You can leave the house. Be careful") if can_leave else speak("You cant leave the house without your mask")


def covid_stat(csv_path):
    # load csv an dataframe
    data = pd.read_csv(csv_path)
    greece = data[data.countriesAndTerritories == "Greece"]
    greece = greece.iloc[::-1]

    # plotting
    fig, (ax1, ax2) = plt.subplots(2)
    fig.suptitle('Covid-19 Greece Stats')
    ax1.plot(greece.dateRep, greece.deaths, color="red")
    ax1.set_xlabel("date")
    ax1.set_ylabel("deaths")
    ax2.plot(greece.dateRep, greece.cases)
    ax2.set_xlabel("date")
    ax2.set_ylabel("cases")
    plt.show()
    time.sleep(5)




SERVICE = authenticate_google()

while True:
    listened_text = get_audio()
    
    if WAKE in listened_text.lower() and not AWAKE:
        obj_face = cl_face.Fac_rec()
        username = obj_face.recogn_user(-1)
        print(username)

        # Get user info
        obj_users_db = user_db.Users_DB()
        name,surname,addr,infected = obj_users_db.user_data("iqmma")
        if infected == "healthy":
            speak(f"Welcome back {name}, how can I help you?")
        else:
            today = dt.today().strftime('%Y-%m-%d')
            delta = dt.strptime(today, '%Y-%m-%d') - dt.strptime(infected, '%Y-%m-%d')
            quarantined_days_left = 15-int(delta.days)
            if(quarantined_days_left > 0):
                print(f"Hello {name}, you have {quarantined_days_left} days quarantined. How can I help you?")
                speak(f"Hello {name}, you have {quarantined_days_left} days quarantined. How can I help you?")
            else:
                obj_users_db.user_cured(username)
                print(f"Hello {name}, you are completely cured. How can I help you?")
                speak(f"Hello {name}, you are completely cured. How can I help you?")
        listened_text = get_audio()
        AWAKE = True

    if AWAKE:
        # Greeting
        for phrase in GREETINGS:
            if phrase in listened_text.lower():
                greetings = ["hey, how can I help you" + name, "hey, what's up?" + name, "I'm listening" + name, "how can I help you?" + name, "hello" + name]
                greet = greetings[random.randint(0,len(greetings)-1)]
                print(greet)
                speak(greet)

        # Ask asis name
        for phrase in ASK_ASIS_NAME:
            if phrase in listened_text.lower():
                print(f"My name is {ASISSTANT_NAME}")
                speak(f"My name is {ASISSTANT_NAME}")

        # Ask time
        for phrase in ASK_TIME:
            if phrase in listened_text.lower():
                time = ctime().split(" ")[3].split(":")[0:2]
                if time[0] == "00":
                    hours = '12'
                else:
                    hours = time[0]
                minutes = time[1]
                time = hours + " hours and " + minutes + "minutes"
                print(time)
                speak(time)

        # Get upcoming events
        for phrase in CALENDAR_STRS:
            if phrase in listened_text.lower():
                date = get_date(listened_text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("Please Try Again")

        # Search Google
        for phrase in SEARCH_GOOGLE:
            if phrase in listened_text.lower():
                search_term = listened_text.split("for")[-1]
                url = "https://google.com/search?q=" + search_term
                webbrowser.get().open(url)
                print("Here is what I found for" + search_term + "on google")
                speak("Here is what I found for" + search_term + "on google")
        

        # Search Youtube
        for phrase in SEARCH_YOUTUBE:
            if phrase in listened_text.lower():
                search_term = listened_text.split("for")[-1]
                search_term = search_term.replace("on youtube","").replace("search","")
                url = "https://www.youtube.com/results?search_query=" + search_term
                webbrowser.get().open(url)
                speak("Here is what I found for " + search_term + "on youtube")

        # Weather
        for phrase in WEATHER:
            if phrase in listened_text.lower():
                search_term = listened_text.split("for")[-1]
                url = "https://www.google.com/search?sxsrf=ACYBGNSQwMLDByBwdVFIUCbQqya-ET7AAA%3A1578847393212&ei=oUwbXtbXDN-C4-EP-5u82AE&q=weather&oq=weather&gs_l=psy-ab.3..35i39i285i70i256j0i67l4j0i131i67j0i131j0i67l2j0.1630.4591..5475...1.2..2.322.1659.9j5j0j1......0....1..gws-wiz.....10..0i71j35i39j35i362i39._5eSPD47bv8&ved=0ahUKEwiWrJvwwP7mAhVfwTgGHfsNDxsQ4dUDCAs&uact=5"
                webbrowser.get().open(url)
                speak("Here is what I found for on google")

        # My current location
        for phrase in ASK_MY_LOCATION:
            if phrase in listened_text.lower():
                Ip_info = requests.get('https://api.ipdata.co?api-key=test').json()
                loc = Ip_info['region']
                print(f"You must be somewhere in {loc}")
                speak(f"You must be somewhere in {loc}")

        # My exact location
        for phrase in ASK_MY_EXACT_LOCATION:
            if phrase in listened_text.lower():
                url = "https://www.google.com/maps/search/Where+am+I+?/"
                webbrowser.get().open(url)
                speak("You must be somewhere near here, as per Google maps")

        # Search wiki
        for phrase in WIKIPEDIA:
            if phrase in listened_text.lower():
                speak("what do you need the definition of")
                while True:
                    try:
                        definition=get_audio()
                    except NameError:
                        speak("Try again")
                    else:
                        break
                
                url=urllib.request.urlopen('https://en.wikipedia.org/wiki/'+definition)
                soup=bs.BeautifulSoup(url,'lxml')
                definitions=[]
                for paragraph in soup.find_all('p'):
                    definitions.append(str(paragraph.text))
                if definitions:
                    print(definitions)
                    if not definitions[0]:
                        speak('im sorry i could not find that definition, please try a web search')
                    elif definitions[1]:
                        speak('here is what i found '+definitions[1])
                    else:
                        speak ('Here is what i found '+definitions[2])
                else:
                        speak("im sorry i could not find the definition for "+definition)

        # Make note with assistant
        for phrase in NOTE_STRS:
            if phrase in listened_text.lower():
                speak("What would you like me to write down? ")
                write_down = get_audio()
                note(write_down)
                speak("I've made a note of that.")

        # Sign Translation
        for phrase in TRANSL_STRS:
            if phrase in listened_text.lower():
                speak("Sign language translation is loading")
                sign_trans_obj = f.SignTranslation()


        # Sleep
        if SLEEP in listened_text.lower():
            AWAKE = False
            speak(f"Bye {name}")

        # Covid Permission
        for phrase in COVID_MSG:
            if phrase in listened_text.lower():
                speak("Tell me the code of corresponding activity")
                covid_codes_help()
                while True:
                    code =get_audio()
                    try:
                        if int(code)>0 and int(code)<=6 :
                            print(f"{code} {name} {addr}")
                            speak("Your message sent")
                            #check if you wear a mask (not made yet)
                            wearing_mask()
                            break
                        else:
                            #code for error
                            pass
                    except:
                        pass

        # Covid Data and PLOT
        for phrase in COVID_STATS:
            if phrase in listened_text.lower():
                covid_stat("Covid-data/data.csv")

    #Developer Mode
    if listened_text.lower() == "developer":
        obj_users_db = user_db.Users_DB()
        speak("Give the developer code")
        code = int(get_audio())
        if (code == DEV_CODE):
            menu = """
            1) Add User
            2) Change Username
            3) Change Address
            4) Got Infected
            """
            print(menu)
            code = int(input("Select from the above(number): "))
            if( code == 1):
               username = input("Username: ")
               name = input("Name: ")
               surname = input("Surname: ")
               addr = input("Address: ")
               obj_users_db.add_user(username,name,surname,addr)
            elif(code == 2):
                old_username = input("Old Username: ")
                username = input("New Username: ")
                obj_users_db.change_username(old_username, username)
            elif (code == 3):
                username = input("Username: ")
                new_addr = input("New Address: ")
                obj_users_db.change_address(username,new_addr)
            elif (code == 4):
                username = input("Username: ")
                obj_users_db.user_got_infected(username)
        else:
            speak("wrong code")








    if QUIT in listened_text.lower():
        sys.exit()
