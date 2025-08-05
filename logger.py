import re
import time
import csv
import os
from datetime import datetime
from nxt.locator import find_one_brick #This is for the lego mindstorms NXT
from nxt.sensor import Ultrasonic, Port #This is also for the lego mindstorms NXT

INVALID_FILENAME_CHARS = '<>:"/\\|?*'

def clean_name(name: str) -> str:
    name = name.strip()
    name = re.sub(f"[{re.escape(INVALID_FILENAME_CHARS)}]", "_", name)
    base = os.path.splitext(name)[0]
    if not base or base in ['.', '']:  # reject extension-only names
        raise ValueError("Filename must include a valid base name.")
    return base + ".csv"

def main():
    try:
        name = input("Enter log filename: ")
        filename = clean_name(name)

        append = False
        if os.path.exists(filename):
            resp = input("File exists. Append? [y/N]: ").lower().strip()
            append = resp == 'y'

        mode = "a" if append else "w"
        with find_one_brick() as brick:
            sensor = Ultrasonic(brick, Port.S4)
            print("Connected to NXT brick.")

            with open(filename, mode, newline='') as f:
                writer = csv.writer(f)
                if not append:
                    f.write("# collected with logger.py v1.2\n")
                    writer.writerow(["t", "distance"])

                print("Logging... Press Ctrl+C to stop.")
                start_time = time.time()

                while True:
                    try:
                        dist = sensor.get_distance()
                        now = time.time() - start_time
                        writer.writerow([now, dist])
                        f.flush()
                        time.sleep(0.05)
                    except KeyboardInterrupt:
                        print("Logging interrupted.")
                        break
                    except Exception as e:
                        print(f"Sensor error: {e}")
                        time.sleep(0.5)  # optional retry pause

    except Exception as e:
        print(f"Setup failed: {e}")

if __name__ == "__main__":
    main()
