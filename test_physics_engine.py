from physics_engine import PhysicsEngine


engine = PhysicsEngine()


# --------------------------------
# TEST ELBOW ANGLE
# --------------------------------

shoulder = (0, 1)
elbow = (0, 0)
wrist = (1, 0)

elbow_angle = engine.get_elbow_angle(
    shoulder,
    elbow,
    wrist
)

print("Elbow Angle:", elbow_angle)


# --------------------------------
# TEST KNEE ANGLE
# --------------------------------

hip = (0, 1)
knee = (0, 0)
ankle = (1, 0)

knee_angle = engine.get_knee_angle(
    hip,
    knee,
    ankle
)

print("Knee Angle:", knee_angle)


# --------------------------------
# TEST VELOCITY
# --------------------------------

previous_position = (0, 0)
current_position = (3, 4)

dt = 2

velocity = engine.get_velocity(
    previous_position,
    current_position,
    dt
)

print("Velocity:", velocity)


# --------------------------------
# TEST ACCELERATION
# --------------------------------

previous_velocity = 2
current_velocity = 6

acceleration = engine.get_acceleration(
    previous_velocity,
    current_velocity,
    dt
)

print("Acceleration:", acceleration)


# --------------------------------
# TEST PROJECTILE
# --------------------------------

speed = 20
angle = 45

projectile = engine.get_projectile_data(
    speed,
    angle
)

print("\nProjectile Data:")

for key, value in projectile.items():
    print(key, ":", value)