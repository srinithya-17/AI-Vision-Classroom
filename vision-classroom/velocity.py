import math


def calculate_distance(p1, p2):
    """Calculate the distance between two (x, y) positions."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx ** 2 + dy ** 2)


def calculate_velocity(p1, p2, dt):
    """Calculate velocity from two positions and elapsed seconds."""
    if dt <= 0:
        return 0.0
    return calculate_distance(p1, p2) / dt


def calculate_acceleration(v1, v2, dt):
    """Calculate acceleration from two velocities and elapsed seconds."""
    if dt <= 0:
        return 0.0
    return (v2 - v1) / dt
