# BreakerMonitor (Raspberry Pi Pico W)

A small MicroPython program for the Raspberry Pi Pico W that periodically publishes a heartbeat message to an MQTT broker. It is intended to run as `main.py` on the Pico W so it starts automatically on boot.

This project is a lightweight building block for a breaker/monitoring system — currently it only reports an "alive" heartbeat over MQTT and flashes the onboard LED as a visual indicator. The code is a good starting point to add actual breaker/sensor inputs and to integrate with Home Assistant or other systems.

Contents
- `main.py` — connects to Wi‑Fi and an MQTT broker, publishes `"alive"` to a configured MQTT topic every N seconds, flashes the onboard LED when the message is published, and handles reconnects.

What the program does
- Connects to Wi‑Fi as a station (STA).
- Creates an MQTT client with a client id based on the Pico's unique_id.
- Connects to the MQTT broker and publishes a retained heartbeat message (payload `alive`) to the configured topic.
- Flashes the Pico W onboard LED 10 times (100 ms per toggle) whenever a heartbeat is published.
- Sends an MQTT ping to keep the connection alive.
- If any error occurs (Wi‑Fi drop, MQTT failure, etc.), disconnects and retries after 5 seconds, recreating the client when possible.

Important behaviors to note
- The heartbeat message is published with `retain=True`. The broker will keep the last heartbeat payload until overwritten.
- Heartbeat interval is configured by `HEARTBEAT_SECONDS` (default 30).
- MQTT credentials are optional; if `MQTT_USER`/`MQTT_PASSWORD` are empty strings they are passed as `None` to the client.
- The MQTT client id is unique per device: `pico-<hex(unique_id)>`.

Configuration (edit main.py)
- WIFI_SSID — your Wi‑Fi SSID (2.4 GHz)
- WIFI_PASSWORD — your Wi‑Fi password
- MQTT_BROKER — IP address or hostname of your MQTT broker
- MQTT_PORT — MQTT port (default 1883)
- MQTT_USER — MQTT username (leave `""` if no auth)
- MQTT_PASSWORD — MQTT password (leave `""` if no auth)
- MQTT_TOPIC — topic to publish the heartbeat to (currently set to `b"homeassistant/sensor/garagebreaker/state"`)
- HEARTBEAT_SECONDS — seconds between heartbeats

Dependencies
- MicroPython firmware for Raspberry Pi Pico W
- umqtt.simple (MicroPython MQTT client)
  - If your MicroPython build doesn't include `umqtt.simple`, copy an implementation (e.g., from micropython-lib) to the device (`umqtt/simple.py`) or upload a compatible MQTT library.

Installing MicroPython on the Pico W
1. Download the Pico W MicroPython UF2 from https://micropython.org.
2. Put the Pico W into bootloader mode and copy the UF2 file onto it.
3. Use Thonny or mpremote to interact with the device.

Uploading files
- Thonny: open `main.py` and save it to the Raspberry Pi Pico device.
- mpremote:
  - mpremote connect /dev/ttyACM0 (or auto)
  - mpremote fs put main.py :/main.py

Running
- With `main.py` on the device root filesystem, the Pico will run it automatically after reset/power-up.
- Use Thonny or a serial terminal (115200 baud) to view prints and debug output.

Example Home Assistant integration (simple)
- The script publishes a retained payload `alive` to a topic. A simple MQTT sensor in Home Assistant can show that message, but to get availability/freshness you should either:
  - Extend the Pico to publish an "online"/"offline" availability topic; or
  - In Home Assistant create a template sensor that considers the timestamp of the last message (or use MQTT Last Will/Retain patterns).
- Minimal sensor example:
  ```yaml
  sensor:
    - platform: mqtt
      name: "Garage Breaker Heartbeat"
      state_topic: "homeassistant/sensor/garagebreaker/state"
      value_template: "{{ value }}"
      qos: 0
  ```
  Note: This will simply display `alive`. For reliable availability use availability topics or a more advanced detection method.

Extending this project
- Add physical breaker/sensor input(s):
  - Use GPIO digital inputs (with pull-up/pull-down) for dry contacts, or an ADC and a properly conditioned current sensor (CT or hall-effect) for current measurement.
  - Publish the breaker state or measured current instead of (or in addition to) the heartbeat.
- Publish JSON payload with timestamps, device id, and sensor values for easier consumption.
- Implement MQTT Last Will and Testament (LWT) to indicate offline status automatically.
- Add an HTTP config interface served by the Pico W to set Wi‑Fi and MQTT via a captive portal/quick setup.
- Add OTA or simple file-based configuration (e.g., `secrets.py` or `config.json`) so credentials are not hard-coded.

Troubleshooting
- If Wi‑Fi doesn't connect:
  - Ensure SSID/password are correct and the network supports 2.4 GHz.
  - Check signal strength and power.
- If MQTT won't connect:
  - Verify broker address and port.
  - Confirm broker allows connections from the device and check credentials.
  - Check if firewall/NAT rules block the Pico from reaching your broker.
- Missing `umqtt.simple` error:
  - Upload a compatible `umqtt` client module to the device.
- Use the serial REPL to view `print()` output and exception tracebacks.

Security and safety notes
- Do not connect mains voltage directly to Pico GPIOs. Use appropriate isolation and sensors (current transformers, optoisolators).
- Keep Wi‑Fi and MQTT credentials secure. Consider using a non-exposed broker or VPN if you're publishing sensitive data.

Quick start checklist
1. Flash MicroPython to the Pico W.
2. Edit `main.py` to set `WIFI_SSID`, `WIFI_PASSWORD`, `MQTT_BROKER`, and optionally user/password and topic.
3. Ensure `umqtt.simple` is available on the device.
4. Upload `main.py` to the Pico W.
5. Reboot the Pico and watch the serial output — you should see connection messages and the LED flashes on each publish.

License
- Add your preferred license to the repository.

If you'd like, I can:
- Add sample code to publish an actual breaker state from a GPIO pin.
- Provide a Home Assistant config that monitors freshness and reports an alarm if the heartbeat stops.
- Create a small `secrets.py` pattern and update `main.py` to import secrets from that file.
