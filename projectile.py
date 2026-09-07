import math


G = 9.81


def calculate_projectile_velocity(speed, angle):
    """
    Calculate horizontal and vertical
    velocity components.
    """

    angle_rad = math.radians(angle)

    vx = speed * math.cos(angle_rad)
    vy = speed * math.sin(angle_rad)

    return vx, vy


def calculate_flight_time(speed, angle):
    """
    Calculate total flight time.

    Assumes launch and landing
    are at the same height.
    """

    angle_rad = math.radians(angle)

    flight_time = (
        2 * speed * math.sin(angle_rad)
    ) / G

    return flight_time


def calculate_max_height(speed, angle):
    """
    Calculate maximum height
    relative to launch point.
    """

    angle_rad = math.radians(angle)

    height = (
        speed ** 2 *
        math.sin(angle_rad) ** 2
    ) / (2 * G)

    return height


def calculate_range(speed, angle):
    """
    Calculate horizontal range.

    Assumes launch and landing
    are at the same height.
    """

    angle_rad = math.radians(angle)

    range_value = (
        speed ** 2 *
        math.sin(2 * angle_rad)
    ) / G

    return range_value