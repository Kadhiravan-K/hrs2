# HRS Raspberry Pi Setup Guide

This guide provides a complete setup process for the Health Registration System (HRS) on a Raspberry Pi 3 Model B+.

## 1. Required components and devices

You will need the following hardware:

- Raspberry Pi 3 Model B+
- MicroSD card (16 GB or larger)
- 5V power supply for Raspberry Pi 3 B+
- HDMI display monitor
- Keyboard and mouse for first-time setup
- Buzzer module
- MLX90614 infrared temperature sensor
- KY-039 pulse/heart-rate sensor
- BME280 environmental sensor
- Jumper wires

## 2. Format the SD card

Use a microSD card that is at least 16 GB in size.

### Recommended format type
- Choose FAT32 for broad compatibility.
- If Raspberry Pi Imager asks for a format option, select the default recommended format.
- If you are formatting manually, use FAT32 so the Raspberry Pi OS installer can write the image properly.

### Recommended process
1. Insert the microSD card into your laptop or desktop using a card reader.
2. Open Raspberry Pi Imager or your system disk tool.
3. Select the card and erase or format it.
4. Choose the default or FAT32 format option.
5. Do not leave any old partitions that could cause boot issues.

## 3. Which operating system to install

Install one of the following:

- Raspberry Pi OS Lite: best for a kiosk-style setup with no desktop.
- Raspberry Pi OS with Desktop: best if you want to use a monitor, keyboard, and mouse easily during setup.

Recommended choice for HRS:
- Raspberry Pi OS Lite if the device will run unattended.
- Raspberry Pi OS with Desktop if you want an easier first-time setup and visual debugging.

## 4. Install Raspberry Pi OS

1. Open Raspberry Pi Imager.
2. Choose Raspberry Pi Device: Raspberry Pi 3.
3. Choose OS: Raspberry Pi OS (32-bit) or Raspberry Pi OS Lite (32-bit).
4. Choose the formatted SD card.
5. Click Write.
6. Wait for the imaging process to finish.
7. Insert the SD card into the Raspberry Pi.
8. Connect the monitor, keyboard, mouse, and power supply.
9. Boot the Raspberry Pi and complete the first-time setup.

## 5. Update the Raspberry Pi system

After the first boot, open the terminal and run:

```bash
sudo apt update
sudo apt upgrade -y
```

## 6. Install Python and required tools

Run:

```bash
sudo apt install -y python3 python3-pip python3-venv git
```

Verify the installation:

```bash
python3 --version
pip3 --version
```

## 7. Transfer the project files from laptop to Raspberry Pi

You can use either of these two methods.

### Method 1: Transfer files using a network connection

If your laptop and Raspberry Pi are on the same network, use SSH:

```bash
scp -r /path/to/hrg2 pi@<raspberry-pi-ip>:/home/pi/
```

Example:

```bash
scp -r C:\Users\YourName\Documents\hrg2 pi@192.168.1.50:/home/pi/
```

### Method 2: Clone from GitHub

If the project is stored in a Git repository, run this on the Raspberry Pi:

```bash
cd /home/pi
git clone <your-repository-url>
```

If the repository is private, use your GitHub credentials or a personal access token.

### Method 3: Copy using an external storage device

You can also copy the project folder to a USB drive and transfer it to the Raspberry Pi manually.

## 8. Raspberry Pi pin connections

Connect the sensors carefully to the correct GPIO pins.

### General safety notes
- Use 3.3V logic where possible.
- Double-check wiring before powering the Pi.
- Do not connect components incorrectly to avoid damaging the board.

### Suggested wiring overview

#### Buzzer module
- VCC → 3.3V or 5V depending on the module
- GND → GND
- SIG/IO → GPIO17

#### MLX90614 infrared temperature sensor
- VIN → 3.3V
- GND → GND
- SCL → GPIO3 (SCL)
- SDA → GPIO2 (SDA)

#### KY-039 pulse/heart-rate sensor
- VCC → 3.3V
- GND → GND
- DO/DAT → GPIO27

#### BME280 environmental sensor
- VIN → 3.3V
- GND → GND
- SCL → GPIO3 (SCL)
- SDA → GPIO2 (SDA)

> If your sensor modules are different, follow the device datasheet and the board labels on the module.

## 9. Open the project folder on the Raspberry Pi

Run:

```bash
cd /home/pi/hrg2
```

## 10. Create a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 11. Install project dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 12. Run the project

Start the application with:

```bash
cd /home/pi/hrg2
source venv/bin/activate
python main.py
```

## 13. Optional: run automatically on boot

If you want the system to start by itself after powering on, add this to the Raspberry Pi crontab:

```bash
crontab -e
```

Then add:

```bash
@reboot /home/pi/hrg2/venv/bin/python /home/pi/hrg2/main.py
```

## 14. Troubleshooting tips

- If Python packages fail to install, run the install step again.
- If the GUI does not appear, check the display cable and resolution.
- If the sensors do not respond, verify the wiring and GPIO pin numbers.
- If the app cannot find the database, make sure the project folder is present and writable.

## 15. Recommended workflow

- Develop the project on your laptop.
- Test it locally.
- Transfer updates to the Raspberry Pi.
- Restart the app after each update.
