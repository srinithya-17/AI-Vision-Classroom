from velocity import (
    calculate_distance,
    calculate_velocity,
    calculate_acceleration
)


# -------------------------
# Distance
# -------------------------

previous_position = (0, 0)
current_position = (3, 4)

distance = calculate_distance(
    previous_position,
    current_position
)


# -------------------------
# Velocity
# -------------------------

dt = 2

velocity = calculate_velocity(
    previous_position,
    current_position,
    dt
)


# -------------------------
# Acceleration
# -------------------------

previous_velocity = 2
current_velocity = 6

acceleration = calculate_acceleration(
    previous_velocity,
    current_velocity,
    dt
)


# -------------------------
# Results
# -------------------------

print("Distance:", distance)
print("Velocity:", velocity)
print("Acceleration:", acceleration)