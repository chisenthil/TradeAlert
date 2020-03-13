from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


scopes = ['https://www.googleapis.com/auth/calendar.events']

flow = InstalledAppFlow.from_client_secrets_file("google_calendar_key.json", scopes=scopes)

flow.run_console()

class GoogleCalendar():

    def __init__(self):
        pass

    def createClandarEvent(self, message):
        self.__create_google_calendar_event(message)

    def __create_google_calendar_event(self, message):
        print("Google Calendar")
