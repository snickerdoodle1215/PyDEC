import requests
import xml.etree.ElementTree as ET
import time
import pygame
import os
import pyttsx3
from datetime import datetime

NWS = "https://api.weather.gov/alerts/active.atom?certainty=Likely%2CPossible&severity=Extreme%2CSevere&urgency=Immediate"

Tone = "chimes.wav"

Log = "log.txt"

pygame.mixer.init()

engine = pyttsx3.init()

def fetch_alerts():
    response = requests.get(NWS)
    if response.status_code == 200:
        return response.text
    else:
        return None

def play_attention_tone():
    pygame.mixer.music.load(Tone)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

def load_processed_alerts():
    if os.path.exists(Log):
        with open(Log, "r") as f:
            return set(f.read().splitlines())
    return set()

def log_processed_alert(alert_id):
    # Append the alert ID to the log file
    with open(Log, "a") as f:
        f.write(alert_id + "\n")

def main():
    processed_alerts = load_processed_alerts()
    engine.setProperty('rate', 150)

    while True:
        alerts = fetch_alerts()
        if alerts:
            root = ET.fromstring(alerts)
            new_alerts = []

            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
                alert_id = entry.find('{http://www.w3.org/2005/Atom}id').text
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

                if alert_id not in processed_alerts:
                    print(f"Emergency alert: {title}")
                    print(f"Details: {summary}" + "\n")
                    print(f"CAP: {link}" +"\n")
                    print(f"Received: " + timestamp)
                    print("_" * 50)

                    log_processed_alert(alert_id)
                    processed_alerts.add(alert_id)
                    new_alerts.append((title, summary))

            if new_alerts:
                play_attention_tone()
                for title, summary in new_alerts:
                    alert_text = f"Here is an urgent message from the National Weather Service: {summary}"
                    engine.say(alert_text)
                engine.runAndWait()

        else:
            print("Failed to receive alerts.")

        time.sleep(10) 

if __name__ == "__main__":
    main()
