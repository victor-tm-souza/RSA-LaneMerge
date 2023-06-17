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
    [40.6443603103219, -8.657333046197893],
    [40.644516458772785, -8.657076358795168],
    [40.64474541472825, -8.656694144010546],
    [40.64498149293546, -8.656294494867327],
    [40.645211464868865, -8.655894845724108]
]

lane2_coordinates = [
    [40.64436605970026, -8.657389003783466],
    [40.64454062638292, -8.657107539474966],
    [40.644768310280604, -8.656727671623232],
    [40.645006423559465, -8.65632198750973],
    [40.64523410586812, -8.655930384993555]
]


speed_km_per_hour = 40
speed_m_per_sec = speed_km_per_hour * (1000/3600)
delay_ms = 50
length_m = 4.3

result_coordinates = []
start_point = 45
needed_acceleration = 0
operation_start_time = 0
merge_timeout = 0

positive_acks = 0
OBU2_coords = []
OBU3_coords = []
change_trajectory = False

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

# coordinates = lane coordinates

def run_along_path(delay):
    global result_coordinates, speed_m_per_sec, change_trajectory
    time_counter = 0
    lane_change = False

    i = 0

    # for coordinate (lat, lon) in lane
    while i < (len(coordinates) - 1):
        current_coord = coordinates[i]
        next_coord = coordinates[i + 1]
        distance = calculate_distance(current_coord, next_coord) * 1000
        time_interval = (distance / speed_m_per_sec)

        # calculate how many position updates will exist between 
        #these 2 coordinates
        num_steps = int(time_interval * 1000 / delay)

        # while it hasn't gone through all steps
        while num_steps >= 1:
            
            # if statement, used to reset steps once the vehicle 
            #path changes from lane 1 to lane 2
            if change_trajectory == False:
                dlat = (next_coord[0] - current_coord[0]) / num_steps
                dlon = (next_coord[1] - current_coord[1]) / num_steps
                
                # Move vehicle by adding to the coordinates
                lat = current_coord[0] + dlat
                lon = current_coord[1] + dlon
                result_coordinates = [lat, lon]
                current_coord = result_coordinates

                # Send info to front-end
                send_message("1 " + str(lat) + " " + str(lon))

                # Generate CAM message
                threading.Thread(target=generate_cam(
                    lat, lon, speed_m_per_sec)).start()
                
                # After an arbitrary timing, decides it wants to merge
                #and sends MCM scheduled_goto
                time_counter += 1
                if (time_counter == start_point):
                    threading.Thread(target=generate_scheduled_goto()).start()

                # 50ms between each position update
                time.sleep(delay / 1000)

                speed_m_per_sec = speed_km_per_hour * (1000/3600)

                distance = calculate_distance(current_coord, next_coord) * 1000
                time_interval = (distance / speed_m_per_sec)
                num_steps = int(time_interval * 1000 / delay)
            
            # If it decided to merge and path was changed
            else:
                i = -1
                change_trajectory = False
                lane_change = True
                break
        i += 1

        # If lane change is complete, send MCM
        #control_state with value "DONE"
        if (lane_change and i == 1):
            threading.Thread(target=generate_control_state("DONE"))
            print("\nMerge over!")


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
    print("Connected vanetza with result code "+str(rc))
    client.subscribe("vanetza/out/cam")


def on_message_vanetza(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf-8'))
    global OBU2_coords, OBU3_coords
    if message["stationID"] == 2:
        OBU2_coords = [message["latitude"], message["longitude"]]
    else:
        OBU3_coords = [message["latitude"], message["longitude"]]


def on_connect_mcm(client, userdata, flags, rc):
    print("Connected mcm with result code "+str(rc))
    client.subscribe("goto_ack")


def on_message_mcm(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf-8'))
    print("\nMesssage: ", msg.topic, "\n", message)
    global positive_acks, needed_acceleration, coordinates, change_trajectory
    if positive_acks < 1:
        if msg.topic == "goto_ack":
            if message["can_proceed"] == True:
                positive_acks += 1
            else:
                print("failed to proceed")
    else:
        if msg.topic == "goto_ack":
            if message["can_proceed"] == True:
                mid_point = calculate_middle_point(
                    OBU2_coords[0], OBU2_coords[1], OBU3_coords[0], OBU3_coords[1])

                future_mid_point = predict_position(
                    lane2_coordinates, mid_point, speed_m_per_sec, 2)

                coordinates = [result_coordinates,
                               [future_mid_point[0], future_mid_point[1]],
                               lane2_coordinates[-1]]

                change_trajectory = True
                threading.Thread(
                    target=generate_control_state("EXECUTING")).start()


def generate_cam(lat, lon, speed):
    f = open('in_cam.json')
    m = json.load(f)
    m["latitude"] = lat
    m["longitude"] = lon
    m["speed"] = speed
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
    socket_message = "1*scheduled_goto*" + m
    send_message_mcm(socket_message)


def generate_control_state(state):
    f = open('control_state.json')
    m = json.load(f)
    m["stationID"] = 1
    m["state"] = state
    m = json.dumps(m)
    client_mcm.publish("control_state", m)
    socket_message = "1*control_state*" + m
    send_message_mcm(socket_message)


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

run_along_path(delay_ms)
