import time, os, sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.JNCScrapper import JNCScrapper

def sleep_until_midnight():
    print("Entering Sleeping Phase")
    current_time = datetime.now()
    target_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0)

    if current_time >= target_time:
        target_time += timedelta(days=1)

    time_difference = target_time - current_time
    seconds_to_wait = time_difference.total_seconds()

    print(f"Waiting for {seconds_to_wait/3600:.2f} hours...")
    try:
        time.sleep(seconds_to_wait)
    except KeyboardInterrupt:
        print("Fin du scrapper")
        sys.exit()


def main():
    load_dotenv(os.path.join(os.getcwd(), ".env"))
    while True:
        scrapper = JNCScrapper()
        scrapper.JNCNina_series()
        sleep_until_midnight()

if __name__ == "__main__":
    main()
