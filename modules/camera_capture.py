"""
Camera Capture Module for Raspberry Pi
Handles automated image capture from PiCamera or USB camera
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Try to import picamera2 (for Pi Camera Module 3), fallback to picamera, then opencv
try:
    from picamera2 import Picamera2
    CAMERA_TYPE = "picamera2"
except ImportError:
    try:
        from picamera import PiCamera
        CAMERA_TYPE = "picamera"
    except ImportError:
        import cv2
        CAMERA_TYPE = "opencv"

class CameraCapture:
    def __init__(self, config_path="config.json"):
        """Initialize camera with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.camera_id = self.config['camera']['camera_id']
        self.location = self.config['camera']['location']
        self.resolution = tuple(self.config['camera']['resolution'])
        self.image_storage_path = Path(self.config['storage']['image_storage_path'])

        # Create storage directory
        self.image_storage_path.mkdir(parents=True, exist_ok=True)

        self.camera = None
        self._initialize_camera()

    def _initialize_camera(self):
        """Initialize the appropriate camera based on available hardware"""
        print(f"🎥 Initializing camera (Type: {CAMERA_TYPE})...")

        if CAMERA_TYPE == "picamera2":
            # For Raspberry Pi Camera Module 3 (newer)
            self.camera = Picamera2()
            config = self.camera.create_still_configuration(
                main={"size": self.resolution}
            )
            self.camera.configure(config)
            self.camera.start()
            time.sleep(2)  # Warm-up time

        elif CAMERA_TYPE == "picamera":
            # For older Raspberry Pi Camera Modules
            self.camera = PiCamera()
            self.camera.resolution = self.resolution
            time.sleep(2)  # Warm-up time

        elif CAMERA_TYPE == "opencv":
            # For USB webcams or when testing without Pi camera
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            time.sleep(1)

        print(f"✅ Camera initialized: {self.camera_id} at {self.location['name']}")

    def capture_image(self, filename=None):
        """
        Capture a single image
        Returns: path to saved image
        """
        timestamp = datetime.now()

        if filename is None:
            filename = f"{self.camera_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"

        image_path = self.image_storage_path / filename

        try:
            if CAMERA_TYPE == "picamera2":
                self.camera.capture_file(str(image_path))

            elif CAMERA_TYPE == "picamera":
                self.camera.capture(str(image_path))

            elif CAMERA_TYPE == "opencv":
                ret, frame = self.camera.read()
                if ret:
                    cv2.imwrite(str(image_path), frame)
                else:
                    raise Exception("Failed to capture frame from webcam")

            print(f"📸 Image captured: {image_path}")

            # Return metadata
            return {
                "image_path": str(image_path),
                "camera_id": self.camera_id,
                "location": self.location,
                "timestamp": timestamp.isoformat(),
                "resolution": self.resolution
            }

        except Exception as e:
            print(f"❌ Capture error: {e}")
            return None

    def capture_timelapse(self, duration_minutes=60, interval_minutes=5):
        """
        Capture images at regular intervals
        """
        print(f"⏱️ Starting timelapse: {duration_minutes}min, every {interval_minutes}min")

        end_time = time.time() + (duration_minutes * 60)
        captures = []

        while time.time() < end_time:
            capture_data = self.capture_image()
            if capture_data:
                captures.append(capture_data)

            # Wait for next interval
            time.sleep(interval_minutes * 60)

        print(f"✅ Timelapse complete: {len(captures)} images captured")
        return captures

    def cleanup(self):
        """Release camera resources"""
        if CAMERA_TYPE == "picamera2":
            self.camera.stop()
        elif CAMERA_TYPE == "picamera":
            self.camera.close()
        elif CAMERA_TYPE == "opencv":
            self.camera.release()

        print("🔒 Camera released")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

# Test function
if __name__ == "__main__":
    print("🌱 Testing Camera Capture Module")

    with CameraCapture("../config.json") as camera:
        # Single capture test
        result = camera.capture_image()
        if result:
            print(f"✅ Test successful!")
            print(json.dumps(result, indent=2))
