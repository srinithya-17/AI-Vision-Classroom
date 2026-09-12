from collections import deque


class GestureSmoother:

    def __init__(
        self,
        buffer_size=12,
        required_ratio=0.70
    ):

        self.history = deque(
            maxlen=buffer_size
        )

        self.required_ratio = required_ratio

        self.current_gesture = "UNKNOWN"


    def update(self, gesture):

        self.history.append(gesture)


        # Count gestures
        counts = {}

        for item in self.history:

            if item not in counts:
                counts[item] = 0

            counts[item] += 1


        if not counts:
            return "UNKNOWN"


        best_gesture = max(
            counts,
            key=counts.get
        )


        best_count = counts[best_gesture]

        required_count = (
            len(self.history)
            * self.required_ratio
        )


        # Only change gesture when
        # enough frames agree.
        if best_count >= required_count:

            self.current_gesture = best_gesture


        return self.current_gesture

    def stability(self):
        """Return the share of recent frames matching the stable gesture."""
        if not self.history or self.current_gesture == "UNKNOWN":
            return 0.0

        matching_frames = sum(
            item == self.current_gesture
            for item in self.history
        )
        return matching_frames / len(self.history)