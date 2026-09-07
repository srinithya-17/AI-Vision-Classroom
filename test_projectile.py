from projectile import (
    calculate_projectile_velocity,
    calculate_flight_time,
    calculate_max_height,
    calculate_range
)


speed = 20
angle = 45


vx, vy = calculate_projectile_velocity(
    speed,
    angle
)

flight_time = calculate_flight_time(
    speed,
    angle
)

max_height = calculate_max_height(
    speed,
    angle
)

range_value = calculate_range(
    speed,
    angle
)


print("Initial Speed:", speed, "m/s")
print("Launch Angle:", angle, "degrees")

print("Horizontal Velocity:", vx, "m/s")
print("Vertical Velocity:", vy, "m/s")

print("Flight Time:", flight_time, "seconds")
print("Maximum Height:", max_height, "meters")
print("Range:", range_value, "meters")