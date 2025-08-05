# 📡 NXT Logger + Analyzer

A Python-based **data logging and analysis** tool for LEGO Mindstorms NXT ultrasonic sensors.  
This project allows you to:
1. **Log** distance data from the ultrasonic sensor in real time.
2. **Analyze** that data to compute velocity, acceleration, and generate comparison plots.

Perfect for robotics experiments, motion profiling, and educational projects.

---

## 🚀 Features

- **Real-time logging** from LEGO NXT ultrasonic sensor (Port S4)
- **Safe CSV writing** with filename sanitization
- Append or overwrite existing logs
- Auto-flushes after each write for data safety
- **Data analysis** with:
  - Moving average filtering
  - Velocity & acceleration calculation
  - Raw vs filtered comparison plots
  - Summary statistics (max velocity, acceleration, total duration)
- **Example outputs** included

---

## 🧰 Requirements

- Python 3.x  
- nxt-python ([GitHub](https://github.com/LEGO-Robotics/NXT-Python) | [PyPI](https://pypi.org/project/nxt-python/))  
- pandas  
- numpy  
- matplotlib  

Install all dependencies:

```bash
pip install -r requirements.txt
````

> 💡 Before starting:
>
> * Turn on your LEGO NXT brick
> * Connect via USB or Bluetooth
> * Install LEGO NXT software so your computer can detect it:
>   [LEGO NXT Software Download](https://education.lego.com/en-us/downloads/retiredproducts/nxt/software)
> * Test connection:
>
> ```bash
> nxt-test
> ```

---

## 📦 File Structure

```
logger.py         # Data logging script
analyzer.py       # Data processing and visualization
requirements.txt  # Python dependencies
examples/         # Sample data and plots
images/           # Physical setup photos
README.md         # Project documentation
.gitignore        # Git hygiene
LICENSE           # Open-source license
```

---

## 📝 How to Use

### 1. Log Data

Run:

```bash
python logger.py
```

* Enter a filename (invalid characters will be replaced with `_`)
* If the file exists, choose `[y]` to append or `[n]` to overwrite
* Press `Ctrl+C` to stop logging

Example CSV output:

```csv
# collected with logger.py v1.2
t,distance
0.01,137
0.07,138
0.12,140
```

---

### 2. Analyze Data

Run:

```bash
python analyzer.py examples/sample_log.csv --window 5
```

* `--window` sets the moving average window size (default: 5 samples)
* Produces:

  * **Processed CSV** with filtered values, velocity, acceleration
  * **Comparison plots** (saved as PNG)
  * **Summary statistics**

Example output:

```
 Stats Summary:
- Duration: 12.53 s
- Max raw velocity:       15.32 cm/s
- Max filtered velocity:  14.87 cm/s
- Max raw acceleration:   35.92 cm/s²
- Max filtered acceleration: 33.10 cm/s²
```

---

## 📊 Example Plot

**Distance (Raw vs Filtered)**
![Sample plot](examples/sample_plot.png)

---

## 📸 Physical Setup

![NXT setup](images/nxt_setup.jpg)
*Ultrasonic sensor mounted on Port S4, connected to NXT brick via USB.*

---

## 📁 Sample Files

Inside the `examples/` folder:

* `sample_log.csv` — Raw logged data
* `processed_sample_log.csv` — Analyzer output
* `sample_plot.png` — Visualization

---

## ⚠️ Notes

* Ultrasonic sensors are sensitive to surface type and angle — expect noise.
* If connection fails, check:

  * Brick is powered on
  * USB/Bluetooth link is active
  * Correct port is specified in `logger.py`
* CSV logs can get large; avoid committing large files to GitHub

---

## 📄 License

MIT License — see `LICENSE` for details.

---

Happy logging & analyzing! 🦾

