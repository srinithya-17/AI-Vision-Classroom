import math


def calculate_distance(p1, p2):
    """
    Calculate distance between two points.

    p1 = previous position (x, y)
    p2 = current position (x, y)
    """

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    distance = math.sqrt(
        dx ** 2 + dy ** 2
    )

    return distance


def calculate_velocity(p1, p2, dt):
    """
    Calculate velocity.

    p1 = previous position
    p2 = current position
    dt = time difference in seconds
    """

    if dt <= 0:
        return 0.0

    distance = calculate_distance(p1, p2)

    velocity = distance / dt

    return velocity


def calculate_acceleration(v1, v2, dt):
    """
    Calculate acceleration.

    v1 = previous velocity
    v2 = current velocity
    dt = time difference in seconds
    """

    if dt <= 0:
        return 0.0

    acceleration = (v2 - v1) / dt

    return acceleration