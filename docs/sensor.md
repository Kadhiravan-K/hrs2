# Sensor Guide

## Supported sensors

The project is designed to work with the following sensors:

- MLX90614 infrared temperature sensor
- BME280 environmental sensor
- KY-039 pulse/heart-rate sensor
- Buzzer module

## Behavior

- The sensor screen reads values on demand.
- If a sensor is unavailable, the app can fall back to demo values.
- Sensor values are stored in the current visit draft.

## Notes

- Wiring must be checked carefully before powering the Raspberry Pi.
- The code is designed to avoid crashing the UI if a sensor library is unavailable.
- The sensor screen shows colors to indicate whether data came from a real sensor or a demo fallback.
