# Health Registration System (HRS)

## Requirements

This document lists the software requirements for developing and running the Health Registration System (HRS).

---

# Python Version

Python 3.13cd /d C:\Users\thewi\Documents\hrg2
py -3.13 -m venv venvcd /d C:\Users\thewi\Documents\hrg2
venv\Scripts\activate.bat

---

# Virtual Environment

A Python virtual environment should be created before installing any dependencies.

Example:

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Upgrade pip

```bash
python -m pip install --upgrade pip
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Python Packages

## Pillow

Used for image loading and GUI assets.

---

## reportlab

Used to generate PDF reports.

---

## tkcalendar

Used for selecting the patient's date of birth.

---

## adafruit-circuitpython-mlx90614

Library for communicating with the MLX90614 infrared temperature sensor.

---

## adafruit-circuitpython-bme280

Library for communicating with the BME280 environmental sensor.

---

## adafruit-blinka

Provides CircuitPython compatibility on Raspberry Pi.

---

## gpiozero

Simplifies Raspberry Pi GPIO programming.

---

## RPi.GPIO

Low-level GPIO access for Raspberry Pi.
---

# Built-in Python Modules

The following modules are included with Python and do not require installation.

- sqlite3
- os
- pathlib
- datetime
- uuid
- json
- shutil
- threading
- logging
- tkinter
- tempfile

---

# Notes

- This project is designed to run locally on a Raspberry Pi 3 Model B+.
- SQLite is used as the local database.
- No internet connection is required during normal operation.
- Reports are generated in PDF format.
- Patient records are stored locally.