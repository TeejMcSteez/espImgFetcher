import os
import requests
import time
from datetime import datetime

url = "http://esp32cam.local/capture"
save_dir = "/home/tj/Desktop/espImages/"  # For Linux
max_retries = 3
max_images = 143  # Set the maximum number of images to keep

# Ensure the save directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

while True:
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                # Check Content-Type header
                content_type = response.headers.get('Content-Type')
                print(f"Content-Type: {content_type}")
                if content_type == 'image/jpeg':
                    image_data = response.content
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    image_filename = f"image-{timestamp}.jpg"
                    image_path = os.path.join(save_dir, image_filename)

                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    print(f"Image Saved: {image_path}")
                    print(f"Received image size: {len(image_data)} bytes")

                    # --- Begin of code to delete old images ---
                    # List all image files in the save directory
                    image_files = [f for f in os.listdir(save_dir) if f.startswith('image-') and f.endswith('.jpg')]

                    # Check if the number of images exceeds the maximum allowed
                    if len(image_files) > max_images:
                        # Sort the files by filename (which includes the timestamp)
                        image_files.sort()
                        # Calculate how many old images need to be deleted
                        num_to_delete = len(image_files) - max_images
                        # Delete the oldest images
                        for i in range(num_to_delete):
                            old_image_filename = image_files[i]
                            old_image_path = os.path.join(save_dir, old_image_filename)
                            try:
                                os.remove(old_image_path)
                                print(f"Deleted old image: {old_image_path}")
                            except Exception as e:
                                print(f"Error deleting file {old_image_path}: {e}")
                    # --- End of code to delete old images ---

                    break  # Exit the retry loop upon successful image capture
                else:
                    print("Response is not an image.")
            else:
                print(f"Status Code: {response.status_code}")
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(.5)
    else:
        print("Max retries reached. Skipping this cycle.")
    time.sleep(.5)
