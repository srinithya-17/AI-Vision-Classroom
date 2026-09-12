from collections import deque


class HandRaiseSmoother:

    def __init__(
        self,
        buffer_size=15,
        required_ratio=0.70
    ):
        self.history = deque(
            maxlen=buffer_size
        )

        self.required_ratio = required_ratio
        self.current_state = False


    def update(self, raised):

        self.history.append(raised)

        if not self.history:
            return False

        raised_count = sum(
            self.history
        )

        required_count = (
            len(self.history)
            * self.required_ratio
        )

        if raised_count >= required_count:
            self.current_state = True

        elif (
            len(self.history) >= 5
            and raised_count == 0
        ):
            self.current_state = False

        return self.current_state

    def stability(self):
        if not self.history:
            return 0.0

        matching_frames = sum(
            item == self.current_state
            for item in self.history
        )
        return matching_frames / len(self.history)