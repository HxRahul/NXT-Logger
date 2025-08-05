import os, csv, time, re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import nxt.locator
import nxt.sensor
import nxt.sensor.generic

# --- Configuration ---
SENSOR_PORT = nxt.sensor.Port.S4
SAMPLE_INTERVAL = 0.05  # 50 ms
INVALID_FILENAME_CHARS = r'<>:"/\\|?!'

# --- Filename Cleaner ---
def clean_name(name: str) -> str:
    name = name.strip()
    name = re.sub(f"[{re.escape(INVALID_FILENAME_CHARS)}]", "_", name)
    if not name:
        return ""
    if not name.lower().endswith(".csv"):
        name += ".csv"
    return name

# --- Log File Selection ---
def choose_log_file():
    while True:
        raw = input("Enter log name: ").strip()
        filename = clean_name(raw)
        if not filename:
            print("Invalid name; try again.")
            continue
        if os.path.exists(filename):
            resp = input(f'"{filename}" exists. Append? [y/n]: ').strip().lower()
            if resp.startswith("y"):
                print(f'Appending to "{filename}"')
                return filename, False
            else:
                print("Choose another name.")
                continue
        else:
            print(f'Creating new file: "{filename}"')
            return filename, True

# --- Live Data Logger ---
def log_data(filename, need_header):
    try:
        with nxt.locator.find() as brick:
            sensor = brick.get_sensor(SENSOR_PORT)
            print("Connected to NXT. Logging... Press Ctrl-C to stop.")

            program_start = time.time()
            prev_time = prev_distance = prev_velocity = None

            with open(filename, "a", newline="") as f:
                writer = csv.writer(f)
                if need_header or os.path.getsize(filename) == 0:
                    writer.writerow(["t (s)", "x_raw (cm)", "v_raw (cm/s)", "a_raw (cm/s²)"])
                    f.flush()

                while True:
                    try:
                        current_time = time.time()
                        elapsed = round(current_time - program_start, 3)
                        distance = sensor.get_sample()

                        velocity = acceleration = np.nan
                        if prev_time is not None:
                            dt = current_time - prev_time
                            if dt > 1e-3:  # avoid divide-by-near-zero
                                dx = distance - prev_distance
                                velocity = dx / dt
                                if prev_velocity is not None:
                                    dv = velocity - prev_velocity
                                    acceleration = dv / dt

                        print(f"{elapsed:.3f}s | Dist: {distance}cm | Vel: {velocity:.2f}cm/s | Accel: {acceleration:.2f}cm/s²")
                        writer.writerow([elapsed, distance, velocity, acceleration])
                        f.flush()

                        prev_time = current_time
                        prev_distance = distance
                        prev_velocity = velocity

                        time.sleep(SAMPLE_INTERVAL)
                    except KeyboardInterrupt:
                        print("\nLogging ended by user.")
                        break
    except Exception as e:
        print(f"Error: {e}")

# --- Data Processor + Plotter ---
def process_and_plot(csv_path, window=5):
    df = pd.read_csv(csv_path)
    df.columns = ["t", "x_raw", "v_raw", "a_raw"]
    df["t"] = pd.to_numeric(df["t"], errors="coerce")
    df.sort_values("t", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Fill missing readings gracefully
    df.fillna(np.nan, inplace=True)

    # Filter: Moving Average
    df["x_filtered"] = df["x_raw"].rolling(window=window).mean().fillna(method="bfill")
    df["v_filtered"] = df["x_filtered"].diff() / df["t"].diff()
    df["a_filtered"] = df["v_filtered"].diff() / df["t"].diff()

    out_csv = "processed_" + csv_path
    df.to_csv(out_csv, index=False)
    print(f"Processed data saved to: {out_csv}")

    # Plotting: 3x2 Grid
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))

    # Distance
    axes[0, 0].plot(df["t"], df["x_raw"], label="Raw", color="blue")
    axes[0, 1].plot(df["t"], df["x_filtered"], label="Filtered", color="green")

    # Velocity
    axes[1, 0].plot(df["t"], df["v_raw"], label="Raw", color="blue")
    axes[1, 1].plot(df["t"], df["v_filtered"], label="Filtered", color="green")

    # Acceleration
    axes[2, 0].plot(df["t"], df["a_raw"], label="Raw", color="blue")
    axes[2, 1].plot(df["t"], df["a_filtered"], label="Filtered", color="green")

    # Labels and legends
    titles = ["Distance vs Time", "Velocity vs Time", "Acceleration vs Time"]
    for i in range(3):
        for j in range(2):
            axes[i, j].set_xlabel("Time (s)")
            axes[i, j].set_ylabel(["Distance (cm)", "Velocity (cm/s)", "Acceleration (cm/s²)"][i])
            axes[i, j].set_title(titles[i] + (" (Raw)" if j == 0 else " (Filtered)"))
            axes[i, j].legend()
            axes[i, j].grid(True)

    plt.tight_layout()
    plot_name = "plot_comparison.png"
    plt.savefig(plot_name)
    plt.show()
    print(f"Graphs saved to: {plot_name}")

# --- Main Entry Point ---
if __name__ == "__main__":
    filename, need_header = choose_log_file()
    log_data(filename, need_header)
    process_and_plot(filename)