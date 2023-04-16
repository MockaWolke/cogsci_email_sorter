import imaplib
import json
import email
import tqdm
import os
from bs4 import BeautifulSoup
import re



def fetch_and_process_email(imap_server, uid):

    result, data = imap_server.uid('fetch', uid, '(RFC822)')
    raw_email = data[0][1]

    if result != 'OK':
        raise ValueError(f"There was this imap error result: {result}")

    email_message = email.message_from_bytes(raw_email)

    return email_message


def get_all_email_udis(imap_server):

    result, data = imap_server.uid('search', None, 'ALL')

    if result != 'OK':
        raise ValueError(f"There was this imap error result: {result}")

    latest_email_uid = data[0].split()

    return latest_email_uid


def get_text_wrapper(email_message):


    try:

        return get_hmtl_text(email_message)

    except InvalidContentTypeError:
        

        return get_plain_text(email_message)



def get_hmtl_text(email_message):

    message = None

    for part in email_message.walk():
        if part.get_content_type() == 'text/html':

            message = part.get_payload(decode=True)
            
            break


    if message is None:
        raise InvalidContentTypeError("No 'text/html' found")

    try:
        decoded = message.decode('utf-8')
        
    except UnicodeDecodeError:
        decoded = message.decode('iso-8859-1')


    soup = BeautifulSoup(decoded, 'html.parser')
    text = soup.get_text()

    text = clean_text(text)

    return text


def get_subject(email_message):

    if isinstance( email_message['Subject'] , str):
        return  email_message['Subject'] 

    try:
        return str( email_message['Subject'] )
    except:
        ValueError("Subject can't be formated to strint")

def get_plain_text(email_message):

    message = None

    for part in email_message.walk():
        if part.get_content_type() == 'text/plain':

            message = part.get_payload(decode=True)
            
            break


    if message is None:
        raise InvalidContentTypeError("No 'text/html' found")

    try:
        decoded = message.decode('utf-8')
        
    except UnicodeDecodeError:
        decoded = message.decode('iso-8859-1')

    return decoded


def replace_multiple_new_lines(text):

    return re.sub(r'\n+', '\n', text)

def replace_multiple_new_tabs(text):

    return re.sub(r'\t+', '\t', text)


def replace_multiple_new_empty(text):

    return re.sub(r' +', ' ', text)

def replace_urls(input_str, url_token = "<URL>"):
    url_pattern = re.compile(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)')

    # Use the sub() method of the regular expression object to replace all URLs with the URL token
    output_str = url_pattern.sub(url_token, input_str)

    url_pattern = re.compile(r'(www\.)[a-zA-Z0-9]+(\.[a-zA-Z]+)+([\/\?\=\&\#]*[a-zA-Z0-9\-\._\?\,\:\'\/\\\+&amp;%\$#\=~])*')

    # Use the sub() method of the regular expression object to replace all URLs with the URL token
    output_str = url_pattern.sub(url_token, input_str)

    return output_str


def clean_text(text):


    text = replace_multiple_new_empty(text)
    text = replace_multiple_new_lines(text)
    text = replace_multiple_new_tabs(text)
    text = replace_urls(text)
    text = re.sub(r'\n +', '\n', text)
    return text


class InvalidContentTypeError(Exception):
    """Exception raised when an email does not include a 'text/html' content type."""
    def __init__(self, message="Email does not include 'text/html' content type."):
        self.message = message
        super().__init__(self.message)
