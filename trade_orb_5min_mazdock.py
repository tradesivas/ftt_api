import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
from datetime import datetime, timedelta
import time
import pytz
import os
from dotenv import load_dotenv
from colorama import Fore, Back, Style
import math
import requests
pd.set_option('mode.copy_on_write', True)

# Load environment variables
load_dotenv(override=True)
tv_userid = os.getenv("tv_userid")
tv_password = os.getenv("tv_password")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("github_username")
REPO_NAME = os.getenv("REPO_NAME")

def sos():
    import winsound
    winsound.Beep(500, 500)

def send_via_github(message):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "event_type": "telegram-message",
        "client_payload": {
            "message": message
        }
    }
    
    response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/dispatches",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 204:
        print("Triggered GitHub workflow successfully to send Telegram msg")
    else:
        print(f"Failed to trigger GitHub workflow to send telegram msg. Status: {response.status_code}, Response: {response.text}")

def wait_market_open():
    # Set market_open to 9 AM today
    market_open = datetime.today().replace(hour=9, minute=15, second=1, microsecond=0)
    market_close = datetime.today().replace(hour=15, minute=30, second=0, microsecond=0)
    current_time = datetime.now()

    if current_time < market_open:
        sleep_time = (market_open - current_time).total_seconds()
        print(f"Wating for Market Open at: {market_open}")
        time.sleep(max(sleep_time, 0))

    print(f"Market Opened")

def next_update():
    # Set market_open to 9 AM today
    market_open = datetime.today().replace(hour=9, minute=15, second=1, microsecond=0)
    market_close = datetime.today().replace(hour=15, minute=30, second=0, microsecond=0)
    current_time = datetime.now()

    if current_time < market_open:
        next_update = market_open
    else:
        delta = current_time - market_open
        total_seconds = delta.total_seconds()
        intervals = int(total_seconds) // 300  # 300 seconds = 5 minutes
        next_update = market_open + timedelta(seconds=(intervals + 1) * 300)

    sleep_time = (next_update - current_time).total_seconds()
    print(f"Next Update: {next_update}")
    time.sleep(max(sleep_time, 0))
def main():
    orb_candle = datetime.today().replace(hour=9, minute=15, second=0, microsecond=0)
    tv = TvDatafeed()
    wait_market_open()
    data = tv.get_hist(symbol="MAZDOCK", exchange="NSE",
                    interval=Interval.in_5_minute, n_bars=80)
    df = pd.DataFrame(data)
    
    # Convert to local timezone
    local_tz = pytz.timezone('Asia/Kolkata')  # Update with your timezone
    now = datetime.now(local_tz)

    # Clean data - remove future bars and incomplete current bar
    df = df[df.index.tz_localize(local_tz) <= now - timedelta(minutes=5)]
    df = df[~df.index.duplicated(keep='last')]

    # Calculate orb values
    orb_high = df.loc[orb_candle, 'high']
    orb_low = df.loc[orb_candle, 'low']
    print(f"{orb_candle} 5 min orb high: {orb_high}")
    print(f"{orb_candle} 5min orb low: {orb_low}")

    while True:
        try:
            # Sleep until next 5-minute mark
            next_update()
            # Fetch fresh data with time validation
            data = tv.get_hist(symbol="MAZDOCK", exchange="NSE",
                            interval=Interval.in_5_minute, n_bars=2)
            df = pd.DataFrame(data)
            print(df)
            
            # Convert to local timezone
            local_tz = pytz.timezone('Asia/Kolkata')  # Update with your timezone
            now = datetime.now(local_tz)
            
            # Clean data - remove future bars and incomplete current bar
            df = df[df.index.tz_localize(local_tz) <= now - timedelta(minutes=5)]
            df = df[~df.index.duplicated(keep='last')]
            print("df after removing incomplete candle")
            print(df)
                          
            # Alert logic
            last_high = df['high'].iloc[-1]
            last_low = df['low'].iloc[-1]
        
            if last_high > orb_high:
                #sos()
                msg = f"{df.index[-1]} NSE:MAZDOCK breaks above 5 min orb high {orb_high}"
                print(Back.RED + Fore.LIGHTYELLOW_EX + msg)
                print(Style.RESET_ALL)
                send_via_github(msg)
            elif last_low < orb_low:
                #sos()
                msg = f"{df.index[-1]} NSE:MAZDOCK breaks below 5 min orb low {orb_high}"
                print(Back.GREEN + Fore.LIGHTYELLOW_EX + msg)
                print(Style.RESET_ALL)
                send_via_github(msg)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(60)
            continue

if __name__ == "__main__":
    main()