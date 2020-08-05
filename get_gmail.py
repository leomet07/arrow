from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = 'https://mail.google.com/'

def get_email(service,n):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """




    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])


    # Call the Gmail API to fetch INBOX
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    print(len(messages))
    message_pairs = []
    for i in range(0,n):
        msg = service.users().messages().get(userId='me', id=messages[i]['id']).execute()
        headers = msg["payload"]["headers"]
        subject = [i['value'] for i in headers if i["name"] == "Subject"][0]
        print(subject)

        sender = [i['value'] for i in headers if i["name"] == "From"][0]
        print(sender)
        message_pairs.append({'sender':sender, "subject": subject})
        print("\n")
    return message_pairs







if __name__ == '__main__':
    message_pairs = get_email(10)
    for pair in message_pairs:
        print(pair)