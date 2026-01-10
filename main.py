import network
import time
from machine import unique_id, Pin
import ubinascii
from umqtt.simple import MQTTClient

WIFI_SSID = "WIFI_SSID"
WIFI_PASSWORD = "WIFI_PASSWORD"

MQTT_BROKER = "MQTT_IP_ADDRESS"
MQTT_PORT = 1883
MQTT_USER = ""      # "" if no auth
MQTT_PASSWORD = ""  # "" if no auth

MQTT_TOPIC = b"homeassistant/sensor/garagebreaker/state"
HEARTBEAT_SECONDS = 30

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    return wlan

def make_client_id():
    return b"pico-" + ubinascii.hexlify(unique_id())

def connect_mqtt():
    print("MQTT Invoked")
    client_id = make_client_id()
    client = MQTTClient(client_id,
                        MQTT_BROKER,
                        port=MQTT_PORT,
                        user=MQTT_USER or None,
                        password=MQTT_PASSWORD or None,
                        keepalive=60)
    client.connect()
    print(client)
    return client

def main():
    print("Starting main")
    connect_wifi()
    

    
    
    client = None

    while True:
        try:
            if client is None:
                client = connect_mqtt()

            # publish heartbeat
            client.publish(MQTT_TOPIC, b"alive", retain=True)
            print("mqtt published")
            # Flash onboard LED when MQTT message is sent is up
            led = Pin("LED", Pin.OUT)
            for i in range(10):
                led.toggle()
                time.sleep_ms(100)
            # simple keep-alive
            client.ping()
            time.sleep(HEARTBEAT_SECONDS)
            

        except Exception as e:
            # on any error, drop client and retry after a short delay
            try:
                if client is not None:
                    client.disconnect()
            except:
                pass
            client = None
            print("sleeping 5 seconds")
            time.sleep(5)

main()

