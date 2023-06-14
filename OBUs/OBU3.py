import time
import math
import websocket
import json
import paho.mqtt.client as mqtt
import threading
from time import sleep
from sharedFunctions import *

# Calculations

coordinates = [
    [40.64439663817633, -8.657339215278627],
    [40.64454062638292, -8.657107539474966],
    [40.644768310280604, -8.656727671623232],
    [40.645006423559465, -8.65632198750973],
    [40.64523410586812, -8.655930384993555]
]

speed_km_per_hour = 40
speed_m_per_sec = speed_km_per_hour * (1000/3600)
delay_ms = 50
length_m = 4.3
safe_distance_m = 14

result_coordinates = []

masterOBU_speed_m_per_second = 0
masterOBU_coordinates = []
masterOBU_id = 0
myId = 3
otherSlave_coordinates = []
needed_acceleration = 0
operation_start_time = 0
operation_timeout = 0
operation_done = False


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


def run_along_path(coordinates, delay):
    global result_coordinates, speed_m_per_sec, operation_done
    first_time = True

    for i in range(len(coordinates) - 1):
        current_coord = coordinates[i]
        next_coord = coordinates[i + 1]
        distance = calculate_distance(current_coord, next_coord) * 1000
        time_interval = (distance / speed_m_per_sec)
        num_steps = int(time_interval * 1000 / delay)

        while num_steps >= 1:
            dlat = (next_coord[0] - current_coord[0]) / num_steps
            dlon = (next_coord[1] - current_coord[1]) / num_steps

            start_time = time.time()
            lat = current_coord[0] + dlat
            lon = current_coord[1] + dlon
            result_coordinates = [lat, lon]
            current_coord = result_coordinates

            send_message("3 " + str(lat) + " " + str(lon))

            threading.Thread(target=generate_cam(
                lat, lon, speed_m_per_sec)).start()

            time.sleep(delay / 1000)

            stop_time = time.time()
            if ((stop_time - operation_start_time) < operation_timeout):
                elapsed_time = stop_time - start_time
                speed_m_per_sec += needed_acceleration * elapsed_time
                operation_done = True
            elif (operation_done):
                if first_time:
                    speed_m_per_sec = masterOBU_speed_m_per_second
                    threading.Thread(target=generate_goto_ack(True))
                    first_time = False
            else:
                speed_m_per_sec = speed_km_per_hour * (1000/3600)

            # new
            distance = calculate_distance(current_coord, next_coord) * 1000
            time_interval = (distance / speed_m_per_sec)
            num_steps = int(time_interval * 1000 / delay)


def send_message(message):
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:7555")  # Replace with the actual server URL
    ws.send(message)
    ws.close()


def send_message_mcm(message):
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:7556")  # Replace with the actual server URL
    ws.send(message)
    ws.close()

# MQTT messages


def on_connect_vanetza(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("vanetza/out/cam")
    # client.subscribe("vanetza/out/denm")
    # ...


def on_message_vanetza(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf-8'))
    global masterOBU_speed_m_per_second, otherSlave_coordinates, masterOBU_coordinates
    if (message["stationID"] == 1):
        masterOBU_speed_m_per_second = message["speed"]
        masterOBU_coordinates = [message["latitude"], message["longitude"]]
    else:
        otherSlave_coordinates = [message["latitude"], message["longitude"]]


def on_connect_mcm(client, userdata, flags, rc):
    print("Connected mcm with result code "+str(rc))
    client.subscribe("scheduled_goto")
    client.subscribe("control_state")


def on_message_mcm(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf-8'))
    print("\nMesssage: ", msg.topic, "\n", message)
    global masterOBU_id, needed_acceleration, operation_timeout, operation_start_time
    if msg.topic == "scheduled_goto":
        masterOBU_id = message["stationID"]
        mid_point = calculate_middle_point(
            result_coordinates[0], result_coordinates[1], otherSlave_coordinates[0], otherSlave_coordinates[1])
        operation_timeout = message["timeout"] - 0.5

        # future_mid_point = predict_position(
        #    coordinates, mid_point, operation_timeout, masterOBU_speed_m_per_second)

        needed_acceleration = calculate_acceleration_2(
            mid_point, result_coordinates, masterOBU_speed_m_per_second, speed_m_per_sec, safe_distance_m, operation_timeout)

        operation_start_time = time.time()

    elif msg.topic == "control_state":
        if message["state"] == "DONE":
            print("\nMerge over!")


def generate_cam(lat, lon, speed):
    f = open('in_cam.json')
    m = json.load(f)
    m["latitude"] = lat
    m["longitude"] = lon
    m["speed"] = int(speed)
    m["length"] = length_m
    m["stationID"] = 3
    m = json.dumps(m)
    client_vanetza.publish("vanetza/in/cam", m)
    f.close()


def generate_goto_ack(proceed):
    f = open('goto_ack.json')
    m = json.load(f)
    m["can_proceed"] = proceed
    m["stationID"] = 3
    m = json.dumps(m)
    client_mcm.publish("goto_ack", m)
    socket_message = "3*goto_ack*" + m
    send_message_mcm(socket_message)


client_vanetza = mqtt.Client()
client_vanetza.on_connect = on_connect_vanetza
client_vanetza.on_message = on_message_vanetza
client_vanetza.connect("192.168.98.13", 1883, 60)

client_mcm = mqtt.Client()
client_mcm.on_connect = on_connect_mcm
client_mcm.on_message = on_message_mcm
client_mcm.connect("localhost", 1100, 60)

threading.Thread(target=client_vanetza.loop_forever).start()
threading.Thread(target=client_mcm.loop_forever).start()

run_along_path(coordinates, delay_ms)
