import cv2
import os
from datetime import datetime
import time

class SimpleESP32Recorder:
    def __init__(self, camera_url, output_dir="recordings"):
        """Initialize the recorder with camera URL and output directory"""
        self.camera_url = camera_url
        self.output_dir = output_dir
        self.cap = None
        self.video_writer = None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def start_recording(self):
        """Start recording from the ESP32-CAM"""
        try:
            # Connect to camera
            print(f"Connecting to camera at {self.camera_url}")
            self.cap = cv2.VideoCapture(self.camera_url)
            
            # Check if camera is opened successfully
            if not self.cap.isOpened():
                print("Error: Could not connect to camera")
                return
            
            # Get video properties
            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = 24  # ESP32-CAM typically runs at 24fps max
            
            # Create video writer
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = os.path.join(self.output_dir, f"recording_{timestamp}.avi")
            
            # Define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(
                video_path, fourcc, fps, (frame_width, frame_height)
            )
            
            print(f"Started recording to {video_path}")
            
            # Main recording loop
            while True:
                ret, frame = self.cap.read()
                if ret:
                    # Add timestamp to frame
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(frame, timestamp, (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Write frame to video file
                    self.video_writer.write(frame)
                else:
                    print("Failed to get frame")
                    break
                    
        except KeyboardInterrupt:
            print("\nRecording stopped by user")
        except Exception as e:
            print(f"Error occurred: {str(e)}")
        finally:
            self.stop_recording()
    
    def stop_recording(self):
        """Clean up resources"""
        if self.video_writer is not None:
            self.video_writer.release()
        if self.cap is not None:
            self.cap.release()
        print("Recording stopped and saved")

def main():
    # You can modify these settings as needed
    CAMERA_URL = "http://192.168.1.100/stream"  # Change to your ESP32-CAM's IP
    OUTPUT_DIR = "recordings"  # Change to your preferred save location
    
    recorder = SimpleESP32Recorder(CAMERA_URL, OUTPUT_DIR)
    
    print("Starting recording... Press Ctrl+C to stop")
    recorder.start_recording()

if __name__ == "__main__":
    main()