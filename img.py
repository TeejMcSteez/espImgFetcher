import requests 
import time
from datetime import datetime 

url = "http://esp32cam.local"
save_dir = "/home/tj/Desktop/espImages/"
max_retries = 3

while True:
	for attempt in range(max_retries):
		try:
			response = requests.get(url, stream=True, timeout=10)
			if response.status_code == 200:
				image_data = b''
				for chunk in response.iter_content(chunk_size=1024):
					if chunk:
						image_data += chunk
				timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
				image_path = f"{save_dir}image-{timestamp}.jpg"
				with open(image_path, 'wb') as f:
					f.write(image_data)
				print(f"Image Saved: {image_path}")
				break
			else:
				print(f"Status Code: {response.status_code}")
		except Exception as e:
			print(f"Attempt {attempt + 1} failed: {e}")
			time.sleep(2)
	else:
		print("Max retires reached. Skipping this cycle.")
	time.sleep(5)
