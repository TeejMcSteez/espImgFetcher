#Ultimately decided to use TCP as the camera cant handle the refresh 1< so I just kept at TCP as that what I get on my network anyways and can upload to http
import os
import socket
import struct
from datetime import datetime, timedelta

# Configuration
save_dir = "C:/Users/teej/Desktop/espImages/"  # Replace with your desired directory
backup_dir = "imgs/"
max_images = 250  # Set the maximum number of images to keep
UDP_IP = ''       # Listen on all available interfaces
UDP_PORT = 50000  # Must match 'remote_port' in your ESP32 code

# Ensure the save directory exists
if not os.path.exists(save_dir):
    os.makedirs(backup_dir)

# Set up the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on UDP port {UDP_PORT}")

# Variables to hold image data
expected_packets = None
received_packets = {}
image_data = bytearray()

# Set a timeout for receiving an entire image
image_timeout = timedelta(seconds=5)
last_packet_time = None

while True:
    try:
        # Set socket timeout
        sock.settimeout(1.0)  # Adjust timeout as necessary

        # Receive packet
        data, addr = sock.recvfrom(2048)  # Adjust buffer size if necessary
        packet_receive_time = datetime.now()

        # Set last_packet_time on receiving the first packet
        if last_packet_time is None:
            last_packet_time = packet_receive_time

        # Extract header information
        if len(data) >= 8:
            packet_number, total_packets = struct.unpack('II', data[:8])
            packet_payload = data[8:]
        else:
            print("Received packet too small to contain header. Ignoring.")
            continue

        # Store the packet payload
        received_packets[packet_number] = packet_payload

        # Set expected total packets if not already set
        if expected_packets is None:
            expected_packets = total_packets
            print(f"Receiving new image from {addr}, expecting {expected_packets} packets.")

        # Progress output
        print(f"Received packet {packet_number + 1}/{expected_packets}")

        # Update last_packet_time
        last_packet_time = packet_receive_time

        # Check if all packets have been received
        if len(received_packets) == expected_packets:
            # Reassemble the image data
            for i in range(expected_packets):
                image_data.extend(received_packets[i])

            # Save the image
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            image_filename = f"image-{timestamp}.jpg"
            image_path = os.path.join(save_dir, image_filename)

            with open(image_path, 'wb') as f:
                f.write(image_data)
            print(f"Image saved: {image_path}")
            print(f"Image size: {len(image_data)} bytes")

            # Manage the number of images
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

            # Clean up for next image
            received_packets.clear()
            expected_packets = None
            image_data = bytearray()
            last_packet_time = None

    except socket.timeout:
        # Check for timeout
        if last_packet_time and (datetime.now() - last_packet_time) > image_timeout:
            print("Image reception timed out. Clearing data and waiting for new image.")
            # Reset variables
            received_packets.clear()
            expected_packets = None
            image_data = bytearray()
            last_packet_time = None
    except Exception as e:
        print(f"Error receiving data: {e}")