import time
import math
import websocket
import json
import paho.mqtt.client as mqtt
import threading
from time import sleep


# Calculations

coordinates = [
    [40.6443603103219, -8.657333046197893],
    [40.644516458772785, -8.657076358795168],
    [40.64474541472825, -8.656694144010546],
    [40.64498149293546, -8.656294494867327],
    [40.645211464868865, -8.655894845724108]
]

speed_km_per_hour = 40
delay_ms = 50
length_m = 4.3
safe_distance_m = 68

result_coordinates = []
start_point = 30

positive_acks = 0


def calculate_safety_distance(speed):
    reaction_time = 1.5
    braking_distance = 0.5 * speed

    safety_distance = speed * reaction_time + braking_distance
    return safety_distance


def calculate_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    radius = 6371  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c
    return distance


def calculate_time_interval(distance, speed):
    duration_hours = distance / speed
    duration_seconds = duration_hours * 3600
    return duration_seconds


def run_along_path(coordinates, speed, delay):
    global result_coordinates
    time_counter = 0
    for i in range(len(coordinates) - 1):
        current_coord = coordinates[i]
        next_coord = coordinates[i + 1]
        distance = calculate_distance(current_coord, next_coord)
        time_interval = calculate_time_interval(distance, speed)
        num_steps = int(time_interval * 1000 / delay)

        dlat = (next_coord[0] - current_coord[0]) / num_steps
        dlon = (next_coord[1] - current_coord[1]) / num_steps

        for j in range(num_steps + 1):
            lat = current_coord[0] + dlat * j
            lon = current_coord[1] + dlon * j
            result_coordinates = [lat, lon]

            send_message("1 " + str(lat) + " " + str(lon))
            generate_cam(lat, lon, speed)
            time_counter += 1
            if (time_counter == start_point):
                threading.Thread(target=generate_scheduled_goto()).start()
            time.sleep(delay / 1000)


def send_message(message):
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:7555")  # Replace with the actual server URL
    ws.send(message)
    ws.close()

# MQTT messages


def on_connect_vanetza(client, userdata, flags, rc):
    print("Connected vanetza with result code "+str(rc))
    client.subscribe("vanetza/out/cam")


def on_message_vanetza(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf-8'))


def on_connect_mcm(client, userdata, flags, rc):
    print("Connected mcm with result code "+str(rc))
    client.subscribe("goto_ack")


def on_message_mcm(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf-8'))
    global positive_acks
    if positive_acks < 1:
        if msg.topic == "goto_ack":
            if message["can_proceed"] == True:
                positive_acks += 1
            else:
                print("failed to proceed")
    else:
        if msg.topic == "goto_ack":
            if message["can_proceed"] == True:
                print("yes!")


def generate_cam(lat, lon, speed):
    f = open('in_cam.json')
    m = json.load(f)
    m["latitude"] = lat
    m["longitude"] = lon
    m_per_sec = speed * (1000 / 3600)
    m["speed"] = int(m_per_sec)
    m["length"] = length_m
    m["stationID"] = 1
    m = json.dumps(m)
    client_vanetza.publish("vanetza/in/cam", m)
    f.close()


def generate_scheduled_goto():
    f = open('scheduled_goto.json')
    m = json.load(f)
    m["stationID"] = 1
    m["timeout"] = 7
    m["lane"] = 2
    m["delayed"] = "FAIL"
    m = json.dumps(m)
    client_mcm.publish("scheduled_goto", m)


client_vanetza = mqtt.Client()
client_vanetza.on_connect = on_connect_vanetza
client_vanetza.on_message = on_message_vanetza
client_vanetza.connect("192.168.98.11", 1883, 60)

client_mcm = mqtt.Client()
client_mcm.on_connect = on_connect_mcm
client_mcm.on_message = on_message_mcm
client_mcm.connect("localhost", 1100, 60)

threading.Thread(target=client_vanetza.loop_forever).start()
threading.Thread(target=client_mcm.loop_forever).start()

run_along_path(coordinates, speed_km_per_hour, delay_ms)
