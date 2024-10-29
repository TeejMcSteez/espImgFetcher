#TODO:
#Find a way to start a little ahead of the total number if images
#in the directory as it doesnt need them all from the start and 
#is required to not cause errors in finding a file that doesnt exist!
import os
import cv2
from PIL import Image
from datetime import datetime

# Define paths
currentPath = os.getcwd()
image_dir = r"/home/tj/Desktop/espImages"
resized_dir = os.path.join(currentPath, 'resized')
video_dir = os.path.join(currentPath, 'Videos')

# Get the current timestamp and format it
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

# Include the timestamp in the video filename
video_name = f"camfootage_{timestamp}.avi"
video_path = os.path.join(video_dir, video_name)

# Ensure directories exist
if not os.path.exists(image_dir):
    print(f"Image directory '{image_dir}' does not exist.")
    exit()

if not os.path.exists(resized_dir):
    os.makedirs(resized_dir)

if not os.path.exists(video_dir):
    os.makedirs(video_dir)

# Initialize variables
mean_height = 0
mean_width = 0

# Get list of image files
valid_extensions = ('.jpg', '.jpeg', '.png')
valid_images = [f for f in os.listdir(image_dir) if f.lower().endswith(valid_extensions)]
num_of_images = len(valid_images)

if num_of_images == 0:
    print("No images found in the directory.")
    exit()

# Start processing images from the 10th one onward
start_index = 9  # This means starting from the 10th image (index 9 since index is 0-based)

# Calculate mean width and height for images from the 10th to the end
for file in valid_images[start_index:]:
    im = Image.open(os.path.join(image_dir, file))
    width, height = im.size
    mean_width += width
    mean_height += height

mean_width = int(mean_width / (num_of_images - start_index))
mean_height = int(mean_height / (num_of_images - start_index))

# Resize images and save to resized directory
for file in valid_images[start_index:]:
    if not os.path.exists(os.path.join(image_dir, file)):
        # Skip if the file has been deleted since listing
        continue
    im = Image.open(os.path.join(image_dir, file))
    im_resized = im.resize((mean_width, mean_height), Image.LANCZOS)
    im_resized.save(os.path.join(resized_dir, file), 'JPEG', quality=99)
    print(f"{file} is resized")

def generate_video():
    images = [img for img in os.listdir(resized_dir)
              if img.lower().endswith(valid_extensions)]
    images.sort()  # Ensure images are in the correct order

    if not images:
        print("No images found in the resized directory.")
        return

    frame = cv2.imread(os.path.join(resized_dir, images[0]))
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    fps = 0.5  # Adjust the frame rate as needed
    video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    for image in images:
        img_path = os.path.join(resized_dir, image)
        if not os.path.exists(img_path):
            # Skip if the file has been deleted since listing
            continue
        frame = cv2.imread(img_path)
        video.write(frame)

    video.release()
    cv2.destroyAllWindows()

    # Remove the resized images directory
    for file in os.listdir(resized_dir):
        os.remove(os.path.join(resized_dir, file))
    os.rmdir(resized_dir)

    print(f"Video saved as {video_path}")

generate_video()
