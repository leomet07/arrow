from __future__ import print_function
import speech_recognition as sr
import os
import time
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pyttsx3
from get_weather_api import get_temperature
from get_weather_api import get_weather
from get_weather_api import get_location
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime
from alarm import play_alarm
from get_gmail import get_email
import subprocess

# If modifying these scopes, delete the file token.pickle.
MAILSCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
MONTHS = [
    "January",
    "Febuary",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            # print("Exeption: " + str(e))
            print("No words said")

    return said


def authenticate_google():

    # this saves credentials
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("mailtoken.pickle"):
        with open("mailtoken.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", MAILSCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("mailtoken.pickle", "wb") as token:
            pickle.dump(creds, token)

    gmailservice = build("gmail", "v1", credentials=creds)

    return service, gmailservice


def get_events(number_of_events_to_get, service):
    # Call the Calendar API
    now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming {} events".format(number_of_events_to_get))
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=number_of_events_to_get,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])
        texttobespoken = str(start)
        # print(texttobespoken)

        dateofevent = int(texttobespoken[8:10])
        monthofevent = int(texttobespoken[5:7])
        # get the month word
        month_asword_ofevent = MONTHS[int(monthofevent) - 1]

        actualtime = str(get_time_by_time_zone())
        actualdate = actualtime[8:10]
        actualmonth = actualtime[5:7]
        # if it is month before double digits convert it to int manually

        print(dateofevent, month_asword_ofevent)

        # get the date and month into a text
        texttobespoken = (
            "You have "
            + str(event["summary"])
            + " on the "
            + str(dateofevent)
            + " of "
            + str(month_asword_ofevent)
        )

        # speak(str(str(start)+ str(event['summary'])))
        speak(texttobespoken)


service, gservice = authenticate_google()


# speak("hello")


def get_time_by_time_zone():
    tf = TimezoneFinder()
    # print('Getting time')

    zip, country_code, con_name, city, lat, long = get_location()
    # print(con_name + "/" + city)

    timezone = tf.timezone_at(lng=long, lat=lat)  # returns 'Europe/Berlin'

    current_conandcity = pytz.timezone(timezone)
    sa_time = datetime.now(current_conandcity)
    # print(sa_time)

    return sa_time


alarmstatus = False


def check(text):
    text = text.lower()
    global alarmstatus
    global timestocheck
    if "calendar" in text:
        get_events(2, service)

        return True

    if "temperature" in text:
        currenttemp = get_temperature()
        speak("The current temperature is: " + str(currenttemp) + " degrees")

        return True

    if "weather" in text:
        currentweather, currenttemp = get_weather()
        speak(
            "The current weather is: "
            + str(currentweather)
            + " with a temparature of "
            + str(currenttemp)
            + " degrees"
        )

        return True

    if "mail" in text:
        try:
            message_pairs = get_email(gservice, 3)
        except:
            print("Email not retriavable")
        for pair in message_pairs:
            speak("You have a message from: " + str(pair["sender"]))
            speak("It's subject is: " + str(pair["subject"]))

        return True

    if "set" in text and "timer" in text:
        print(text)

        # search from end to beg
        first_found = text.rfind("timer")
        # add the length of the word for everything not regarding the triggerin gof the bopt
        first_found += len("timer")
        print(first_found)

        nontrigger = text[first_found:]
        print(nontrigger)

        nontrigger_no_space = nontrigger.replace(" ", "")
        print(nontrigger_no_space)

        # get the last speakim of minutes
        last_of_minutes = nontrigger_no_space.rfind("minute")
        print(nontrigger_no_space[last_of_minutes:])

        # get the two digits before the word minutes (the amount of minutes)
        minute_amount = nontrigger_no_space[last_of_minutes - 2 : last_of_minutes]
        print("Pure minue amount" + str(minute_amount))
        # if the minute amount is single digit then then edit the variable to only take that digit
        if not (minute_amount.isdigit()):
            print("Contains chars")
            minute_amount = nontrigger_no_space[last_of_minutes - 1 : last_of_minutes]
        print("Minute amount: " + str(minute_amount))

        # convert the minute amount to an int
        minute_amount = int(minute_amount)
        # print(str(minute_amount) + str(type(minute_amount)))

        # get current time
        print("getting the time")
        datetime_string = str(get_time_by_time_zone())
        print(datetime_string)

        minutes_from_current_time = ((datetime_string.split())[1])[3:5]
        print(minutes_from_current_time)

        hour_from_current_time = ((datetime_string.split())[1])[0:2]
        print(hour_from_current_time)

        minute_to_ring_at = int(minutes_from_current_time) + minute_amount
        print(minute_to_ring_at)

        hour_to_ring_at = int(hour_from_current_time)

        # if the  minurte to rimg at goesover 59 minute, add 1 hour
        if minute_to_ring_at > 59:
            minute_to_ring_at -= 60
            hour_to_ring_at += 1
        print(hour_to_ring_at, minute_to_ring_at)

        hour_to_ring_at_formatted = str(hour_to_ring_at)
        # if string is single didgit add a zero ti the beggining
        if len(hour_to_ring_at_formatted) < 2:
            print("Adding a zero to formatted hour")
            hour_to_ring_at_formatted = "0" + hour_to_ring_at_formatted

        minute_to_ring_at_formatted = str(minute_to_ring_at)
        if len(minute_to_ring_at_formatted) < 2:
            print("Adding a zero to formatted minute")
            minute_to_ring_at_formatted = "0" + minute_to_ring_at_formatted
        time_to_ring_at = (
            ((datetime_string.split())[0])
            + " "
            + str(hour_to_ring_at_formatted)
            + ((datetime_string.split())[1])[2:3]
            + str(minute_to_ring_at_formatted)
            + ((datetime_string.split())[1])[5:]
        )
        print(datetime_string + "    " + time_to_ring_at)

        timestocheck.append(time_to_ring_at)

        return True
    if "time" in text:

        time = str(get_time_by_time_zone())
        print(time)

        hour = ((time.split())[1])[0:2]
        min = ((time.split())[1])[3:5]
        print(hour, min)
        # min = "00"
        displayh = hour
        displaymin = min
        timeofday = ""

        if int(hour) > 12:
            displayh = str(int(displayh) - 12)
            timeofday = "PM"
        elif int(hour) == 12:
            timeofday = "PM"
        else:
            timeofday = "AM"
        # formstting the time to sound human
        if str(min) == "00":
            displaymin = "o'clock"

            # u dont say am or pm with o clock
            timeofday = ""
        displaytime = "The time is {} {} {}".format(displayh, displaymin, timeofday)
        speak(str(displaytime))

        return True

    if "stop" in text and ("alarm" in text or "timer" in text):
        print("alarm here")
        alarmstatus = False
        timestocheck = []

        return True

    if "open" in text:

        print("oprning..")

        try:
            """
            print(text[text.find('open') + len("open") + 1:len(text)])
            print(apps[text[text.find('open') + len("open") + 1:len(text)]])
            app = subprocess.Popen(apps[text[text.find('open') + len("open") + 1:len(text) ]]["path"])
            """
            for key_name, value in apps.items():
                print(
                    key_name
                )  # The key is stored in whatever you called the first variable.
                print(
                    value
                )  # The value associated with that key is stored in your second variable.
                if key_name in text:
                    app = subprocess.Popen(value["path"])

        except:
            pass
        return True

    if "quit" in text or "close" in text or "exit" in text:
        # subprocess.call(["taskkill", "/K", "/IM", "word.exe"])
        for key_name, value in apps.items():
            print(
                key_name
            )  # The key is stored in whatever you called the first variable.
            print(
                value
            )  # The value associated with that key is stored in your second variable.
            if key_name in text:
                result = os.system("taskkill /im " + value["name"] + " /f")
        return True

    return False


apps = {
    "excel": {
        "path": [r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE"],
        "name": "EXCEL.EXE",
    },
    "word": {
        "path": [r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"],
        "name": "WINWORD.EXE",
    },
}


def checktime(times):
    print("checkimg the time")
    global alarmstatus
    if len(times) > 0:
        for i in times:
            # getting the time rn
            currenttime = get_time_by_time_zone()

            # get the time to compare against into datetime by modeling it on the curtrent time
            hour = ((i.split())[1])[0:2]
            min = ((i.split())[1])[3:5]
            timezoneoffset = (i[25:]).replace(":", "")
            checkagainst = (
                datetime.strptime(
                    str(i[0:25] + timezoneoffset), "%Y-%m-%d %H:%M:%S.%f%z"
                )
            ).replace(hour=int(hour), minute=int(min), second=0, microsecond=0)
            print(currenttime, checkagainst)
            if currenttime >= checkagainst:
                print("over")
                alarmstatus = True


triggerword = "arrow"
triggerword = triggerword.lower()
# timestocheck =["2019-11-18 19:35:21.627013-05:00"]
timestocheck = []
# amunt of trys to retry
retry_min = 1
# speak("starting")
while True:
    checktime(timestocheck)

    print("\n")
    print("Listening...")
    text = get_audio()
    text = text.lower()

    words = text.split()
    # if only hello said and text will be said later

    if text[len(triggerword) * -1 : len(triggerword)] == triggerword:
        retry_amount = 0
        while retry_amount < retry_min:
            retry_amount += 1
            checkstatus = True
            print("Triggered")
            speak("What can I do for you? ")
            text = get_audio()
            # if nothing said listen again
            if text == "":
                continue

            print("listening")
            if not ("exit" in text):

                checkstatus = check(text)
                if not (checkstatus):
                    speak("I dont know that, please ask again:")
                    print("I dont know that one")
                else:
                    break

    elif len(text) > len(triggerword):
        if triggerword in text:
            print("Alt trigger")

            checkstatus = check(text)
            if not (checkstatus):
                speak("I dont know that: Ask again:")

    if alarmstatus:
        print("Ring Ring")
        play_alarm()

