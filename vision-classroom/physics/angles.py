import math


def calculate_angle(a, b, c):
    """
    Calculate the angle ABC in degrees.

    a = first point
    b = middle/joint point
    c = third point
    """

    ba_x = a.x - b.x
    ba_y = a.y - b.y

    bc_x = c.x - b.x
    bc_y = c.y - b.y

    dot_product = (
        ba_x * bc_x
        + ba_y * bc_y
    )

    magnitude_ba = math.sqrt(
        ba_x ** 2
        + ba_y ** 2
    )

    magnitude_bc = math.sqrt(
        bc_x ** 2
        + bc_y ** 2
    )

    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0.0

    cosine_angle = (
        dot_product
        / (magnitude_ba * magnitude_bc)
    )

    # Prevent floating-point errors
    cosine_angle = max(
        -1.0,
        min(1.0, cosine_angle)
    )

    angle = math.degrees(
        math.acos(cosine_angle)
    )

    return angle