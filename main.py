import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SENDER = os.getenv("SENDER")


def check_email(username, password, sender_email):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")

    # Search unread emails from specific sender
    status, messages = mail.search(None, f'(UNSEEN FROM "{sender_email}")')
    email_ids = messages[0].split()

    for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                return msg
    return None

def extract_accept_link(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/html":
                body = part.get_payload(decode=True).decode(errors="ignore")
                soup = BeautifulSoup(body, "html.parser")
                for a in soup.find_all('a', href=True):
                    if "accept" in a.text.lower() or "accept" in a['href'].lower():
                        return a['href']
    return None

def click_accept_button(url):
    driver = webdriver.Chrome()  # Requires chromedriver installed and in PATH
    driver.get(url)
    # Optionally wait or perform more actions
    time.sleep(5)  # Give time for the page to load
    driver.quit()

def main():
    while True:
        print("Checking for new email...")
        msg = check_email(EMAIL, PASSWORD, SENDER)
        if msg:
            print("Email found from sender.")
            link = extract_accept_link(msg)
            if link:
                print(f"Accept link found: {link}")
                click_accept_button(link)
            else:
                print("No accept link found.")
        else:
            print("No new emails.")
        time.sleep(60)  # Wait a minute before checking again

if __name__ == "__main__":
    main()
