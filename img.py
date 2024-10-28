#TODO
#I want to add a feature where python smashes the imgs into a video for playback every 2 minutes (for now)
#Wanna use the video playback to display to a http page of every x minute sequence for the past day (ish)
import os
import requests
#import time?
from datetime import datetime

url = "http://esp32cam.local/capture"
#save_dir = "/home/tj/Desktop/espImages/"  # For Linux
#save_dir = "C:/Users/teej/OneDrive/Desktop/espImages/"  # For Windows Laptop
save_dir = "C:/Users/teej/Desktop/espImages/"  # For Windows PC
max_retries = 3 # Max numbers of retries before closing connection 
max_images = 250  # Set the maximum number of images to keep

# Ensure the save directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

while True:
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=1)
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

                    image_files = [f for f in os.listdir(save_dir) if f.startswith('image-') and f.endswith('.jpg')]

                    if len(image_files) > max_images:
                        image_files.sort()
                        num_to_delete = len(image_files) - max_images
                        for i in range(num_to_delete):
                            old_image_filename = image_files[i]
                            old_image_path = os.path.join(save_dir, old_image_filename)
                            try:
                                os.remove(old_image_path)
                                print(f"Deleted old image: {old_image_path}")
                            except Exception as e:
                                print(f"Error deleting file {old_image_path}: {e}")

                    break  # Exit the retry loop upon successful image capture
                else:
                    print("Response is not an image.")
            else:
                print(f"Status Code: {response.status_code}")
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            #time.sleep(1)
    else:
        print("Max retries reached. Skipping this cycle.")
    #time.sleep(1)
