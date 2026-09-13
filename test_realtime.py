from physics_engine import PhysicsEngine


class Landmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Create physics engine
engine = PhysicsEngine()

# Simulated MediaPipe landmarks
landmarks = [Landmark(0, 0) for _ in range(33)]

# Set important body landmarks
landmarks[11] = Landmark(0.4, 0.3)   # left shoulder
landmarks[13] = Landmark(0.4, 0.5)   # left elbow
landmarks[15] = Landmark(0.5, 0.5)   # left wrist

landmarks[23] = Landmark(0.4, 0.6)   # left hip
landmarks[25] = Landmark(0.4, 0.8)   # left knee
landmarks[27] = Landmark(0.4, 1.0)   # left ankle


# Frame 1
result1 = engine.process_landmarks(landmarks, 0.0)

print("Frame 1:")
print(result1)


# Move wrist for Frame 2
landmarks[15] = Landmark(0.6, 0.5)

# Frame 2
result2 = engine.process_landmarks(landmarks, 0.033)

print("\nFrame 2:")
print(result2)