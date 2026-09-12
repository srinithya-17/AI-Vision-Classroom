import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class PoseTracker:

    def __init__(self, model_path):

        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.detector = (
            vision.PoseLandmarker
            .create_from_options(options)
        )


    def detect(self, frame, timestamp_ms):

        rgb_frame = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame
        )

        result = self.detector.detect_for_video(
            rgb_frame,
            timestamp_ms
        )

        return result


    def close(self):

        self.detector.close()