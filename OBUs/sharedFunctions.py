from math import radians, sin, cos, sqrt, asin
from math import *


def calculate_middle_point(lat1, lon1, lat2, lon2):
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    avg_lat = (lat1_rad + lat2_rad) / 2

    avg_lon = (lon1_rad + lon2_rad) / 2

    avg_lat_deg = degrees(avg_lat)
    avg_lon_deg = degrees(avg_lon)

    return avg_lat_deg, avg_lon_deg


def calculate_acceleration_1(coord_a, coord_b, speed_a, speed_b, distance, time):

    # Calculate the initial distance between the vehicles
    initial_distance = calculate_distance(coord_a, coord_b)

    # Calculate the relative displacement between Vehicle A and Vehicle B
    displacement = initial_distance - distance

    # Calculate the relative speed between Vehicle A and Vehicle B
    relative_speed = speed_a - speed_b

    # Calculate the required acceleration
    acceleration = (2 * displacement) / (time ** 2) - \
        (2 * relative_speed) / (time**2)

    return acceleration


def calculate_acceleration_2(coord_a, coord_b, speed_a, speed_b, distance, time):

    # Calculate the initial distance between the vehicles
    initial_distance = calculate_distance(coord_a, coord_b)

    # Calculate the relative displacement between Vehicle A and Vehicle B
    displacement = distance - initial_distance

    # Calculate the relative speed between Vehicle A and Vehicle B
    relative_speed = speed_b - speed_a

    # Calculate the required acceleration
    acceleration = (2 * displacement) / (time ** 2) - \
        (2 * relative_speed) / (time**2)

    return acceleration


def calculate_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    radius = 6371  # Earth's radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) * sin(dlat / 2) + cos(radians(lat1)) * \
        cos(radians(lat2)) * sin(dlon / 2) * sin(dlon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = radius * c
    return distance * 1000


def predict_position(line_coordinates, initial_position, speed, time):
    # Calculate the total distance of the line segment
    total_distance = sum([calculate_distance([lat1, lon1], [lat2, lon2])
                         for (lat1, lon1), (lat2, lon2) in zip(line_coordinates[:-1], line_coordinates[1:])])

    # Calculate the distance covered by the vehicle after the specified time
    distance_covered_partial = speed * time
    distance_covered = calculate_distance(
        line_coordinates[0], initial_position) + distance_covered_partial

    # Find the segment of the line where the vehicle will be after the specified time
    current_distance = 0
    for (lat1, lon1), (lat2, lon2) in zip(line_coordinates[:-1], line_coordinates[1:]):
        segment_distance = calculate_distance([lat1, lon1], [lat2, lon2])
        if current_distance + segment_distance > distance_covered:
            # Calculate the interpolation factor based on the remaining distance within the segment
            remaining_distance = distance_covered - current_distance
            factor = remaining_distance / segment_distance

            # Calculate the predicted position using linear interpolation
            initial_lat, initial_lon = initial_position
            predicted_lat = initial_lat + factor * (lat2 - initial_lat)
            predicted_lon = initial_lon + factor * (lon2 - initial_lon)
            return predicted_lat, predicted_lon
        current_distance += segment_distance

    # If the distance covered exceeds the total distance of the line segment,
    # return the last point of the line as the predicted position
    return line_coordinates[-1]
