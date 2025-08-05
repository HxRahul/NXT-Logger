#!/usr/bin/env python3
"""

Loads raw distance log CSV (handles mixed encodings),
computes raw & filtered distance, velocity, acceleration,
then outputs processed CSV + 3×2 comparison plots.
"""

import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def moving_average(signal: pd.Series, window: int) -> pd.Series:
    return signal.rolling(window=window, center=True, min_periods=1).mean()

def safe_sample_rate(df: pd.DataFrame) -> float:
    avg_dt = df["dt"].mean()
    return round(1 / avg_dt, 1) if pd.notna(avg_dt) and avg_dt > 0 else float("nan")

def summarize_stats(df: pd.DataFrame) -> None:
    print("\n Stats Summary:")
    print(f"- Duration: {df['t'].max():.2f} s")
    print(f"- Max raw velocity:       {df['velocity_raw'].max(skipna=True):.2f} cm/s")
    print(f"- Max filtered velocity:  {df['velocity_f'].max(skipna=True):.2f} cm/s")
    print(f"- Max raw acceleration:   {df['acceleration_raw'].max(skipna=True):.2f} cm/s²")
    print(f"- Max filtered acceleration: {df['acceleration_f'].max(skipna=True):.2f} cm/s²")

def make_plots(df: pd.DataFrame, window: int, sample_rate: float, base: str):
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    titles = ["Distance (cm)", "Velocity (cm/s)", "Acceleration (cm/s²)"]
    raw_cols = ["distance", "velocity_raw", "acceleration_raw"]
    filt_cols = ["distance_f", "velocity_f", "acceleration_f"]

    for i in range(3):
        # Raw
        axes[i, 0].plot(df["t"], df[raw_cols[i]], color="blue", label="Raw")
        axes[i, 0].set_title(f"{titles[i]} vs Time (Raw)")
        axes[i, 0].set_xlabel("Time (s)")
        axes[i, 0].set_ylabel(titles[i])
        axes[i, 0].grid(True)

        # Filtered
        axes[i, 1].plot(df["t"], df[filt_cols[i]], color="green", label="Filtered")
        axes[i, 1].set_title(f"{titles[i]} vs Time (Filtered)")
        axes[i, 1].set_xlabel("Time (s)")
        axes[i, 1].set_ylabel(titles[i])
        axes[i, 1].grid(True)

    # Add a small annotation in the top-right plot
    axes[0, 1].text(
        0.05, 0.9,
        f"w={window}, sr≈{sample_rate}Hz",
        transform=axes[0, 1].transAxes,
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.6)
    )

    plt.tight_layout()
    plotname = f"plot_comparison_{base}_w{window}_sr{sample_rate}.png"
    plt.savefig(plotname)
    print(f" Saved comparison plots as: {plotname}")
    plt.show()

def analyze(csv_file: str, window: int) -> None:
    # Attempt UTF-8 then Latin-1
    for enc in ("utf-8", "latin1"):
        try:
            df = pd.read_csv(csv_file, comment="#", encoding=enc)
            print(f"Loaded '{csv_file}' with encoding: {enc}")
            break
        except UnicodeDecodeError:
            print(f"  Encoding {enc!r} failed, trying next…")
        except Exception as e:
            print(f" Error reading '{csv_file}' with {enc!r}: {e}")
            return
    else:
        print(" All encoding attempts failed. Check file encoding.")
        return

    # Normalize headers & rename x_raw→distance if present
    df.columns = df.columns.str.replace(r"\s*\(.*\)", "", regex=True).str.strip()
    df.rename(columns={"x_raw": "distance"}, inplace=True)

    # Validate
    if not all(col in df.columns for col in ["t", "distance"]):
        print(f" CSV missing required columns. Found: {list(df.columns)}")
        return

    # Compute dt
    df["dt"] = df["t"].diff()
    df = df[df["dt"] > 1e-4].reset_index(drop=True)

    # Raw derivatives
    df["velocity_raw"]      = df["distance"].diff()     / df["dt"]
    df["acceleration_raw"]  = df["velocity_raw"].diff() / df["dt"]

    # Filtered distance & recalc
    df["distance_f"] = moving_average(df["distance"], window)
    df["velocity_f"]     = df["distance_f"].diff()     / df["dt"]
    df["acceleration_f"] = df["velocity_f"].diff()     / df["dt"]

    # Clean infinities
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Save processed CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    base = os.path.splitext(os.path.basename(csv_file))[0]
    out_csv = f"processed_{base}_w{window}_{timestamp}.csv"
    df.to_csv(out_csv, index=False)
    print(f" Saved processed data to: {out_csv}")

    # Plot & summarize
    sample_rate = safe_sample_rate(df)
    make_plots(df, window, sample_rate, base)
    summarize_stats(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze NXT ultrasonic log")
    parser.add_argument("csv_file", help="CSV file to analyze")
    parser.add_argument(
        "--window", "-w", type=int, default=5,
        help="Rolling-average window size (samples)"
    )
    args = parser.parse_args()
    analyze(args.csv_file, args.window)