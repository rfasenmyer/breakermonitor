import network
import time
from machine import unique_id, Pin
import ubinascii
from umqtt.simple import MQTTClient

WIFI_SSID = "WIFI_SSID"
WIFI_PASSWORD = "WIFI_PASSWORD"
MQTT_BROKER = "MQTT_IP_ADDRESS"
MQTT_PORT = 1883
MQTT_USER = ""  # "" if no auth
MQTT_PASSWORD = ""  # "" if no auth
MQTT_TOPIC = b"homeassistant/sensor/garagebreaker/state"
HEARTBEAT_SECONDS = 30

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
        print("WiFi connected")
    return wlan

def make_client_id():
    return b"pico-" + ubinascii.hexlify(unique_id())

def connect_mqtt():
    print("MQTT Invoked")
    client_id = make_client_id()
    client = MQTTClient(client_id, MQTT_BROKER, port=MQTT_PORT, 
                       user=MQTT_USER or None, password=MQTT_PASSWORD or None, 
                       keepalive=60)
    client.connect()
    # Test connection with ping
    client.ping()
    print("MQTT connected and verified")
    return client

def main():
    print("Starting main")
    wlan = connect_wifi()
    client = None
    message_count = 0
    
    while True:
        try:
            # Check WiFi connection
            if not wlan.isconnected():
                print("WiFi disconnected, reconnecting...")
                wlan = connect_wifi()
                client = None  # Force MQTT reconnection
            
            # Force fresh MQTT connection every 10 messages to prevent stale connections
            if client is None or message_count % 10 == 0:
                if client is not None:
                    try:
                        client.disconnect()
                    except:
                        pass
                client = connect_mqtt()
                print(f"Fresh MQTT connection established (msg #{message_count})")
            
            # Publish with timestamp for debugging
            timestamp = time.ticks_ms()
            message = f"alive_{timestamp}".encode()
            client.publish(MQTT_TOPIC, message, retain=True)
            
            # Verify broker received it with ping
            client.ping()
            print(f"mqtt published and verified: {message}")
            message_count += 1
            
            # Flash onboard LED when MQTT message is sent
            led = Pin("LED", Pin.OUT)
            for i in range(10):
                led.toggle()
                time.sleep_ms(100)
            
            time.sleep(HEARTBEAT_SECONDS)
            
        except Exception as e:
            print(f"Error: {e}")
            # Reset connections on any error
            try:
                if client is not None:
                    client.disconnect()
            except:
                pass
            client = None
            print("sleeping 5 seconds")
            time.sleep(5)

main()
