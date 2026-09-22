import math


G = 9.81


def calculate_projectile_velocity(speed, angle):
    angle_rad = math.radians(angle)
    return speed * math.cos(angle_rad), speed * math.sin(angle_rad)


def calculate_flight_time(speed, angle):
    return (2 * speed * math.sin(math.radians(angle))) / G


def calculate_max_height(speed, angle):
    return (speed ** 2 * math.sin(math.radians(angle)) ** 2) / (2 * G)


def calculate_range(speed, angle):
    return (speed ** 2 * math.sin(2 * math.radians(angle))) / G
