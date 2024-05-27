import cv2
import numpy as np
import os
import time
from PIL import Image, ImageDraw, ImageFont
import pyvirtualcam
from pyvirtualcam import PixelFormat
import threading
import queue
from collections import deque

# Initialisation de la caméra
realCam = cv2.VideoCapture(0)

# Paramètres de l'ASCII art
block_font_size = 4 # Ajuster pour la résolution de l'image
ascii_chars = " .':^+*#M%@$"
ascii_chars_images = {}
font_path = "Consolas.ttf"

ascii_art = ""
old_ascii_art = ""

imageReturn = None
draw = None

# Charger une police de caractères monospacée
font = ImageFont.truetype(font_path, block_font_size)

# Effacer le terminal une seule fois avant la boucle principale
os.system('cls' if os.name == 'nt' else 'clear')

def setup():
    global imageReturn
    global draw
    global ascii_art
    global old_ascii_art

    for ascii_char in ascii_chars:
        char_image = Image.new('RGB', (block_font_size, block_font_size), color=(30, 30, 30))
        char_draw = ImageDraw.Draw(char_image)
        char_draw.text((0, 0), ascii_char, font=font, fill=(250, 250, 250))
        ascii_chars_images[ascii_char] = char_image

    # Generate an initial ASCII art to determine the size
    ret, initial_image = realCam.read()
    if not ret:
        raise RuntimeError("Failed to capture image from camera during setup.")

    image_to_ascii(initial_image)
    lines = ascii_art.split('\n')

    width_obs = max(len(line) for line in lines) * block_font_size
    height_obs = len(lines) * block_font_size

    imageReturn = Image.new('RGB', (width_obs, height_obs), color=(30, 30, 30))
    draw = ImageDraw.Draw(imageReturn)

    # Initialiser old_ascii_art avec la même taille que ascii_art
    old_ascii_art = '\n'.join([' ' * len(line) for line in lines])

def image_to_ascii(image):
    global ascii_art

    # Resize the image using nearest neighbor approach
    small_image = image[::block_font_size, ::block_font_size]
    
    # Convert the small image to grayscale
    grayscale_image = np.mean(small_image, axis=2)
    
    # Normalize grayscale image to match the range of ascii_chars
    normalized_image = (grayscale_image / 255 * (len(ascii_chars) - 1)).astype(int)
    
    # Create ASCII art by mapping the normalized image to ascii characters
    ascii_art = "\n".join(
        " ".join(ascii_chars[pixel] for pixel in row)
        for row in normalized_image
    )

def ascii_to_image():
    global old_ascii_art

    lines = ascii_art.split('\n')
    old_lines = old_ascii_art.split('\n')

    y = 0
    for new_line, old_line in zip(lines, old_lines):
        x = 0
        for new_char, old_char in zip(new_line, old_line):
            if new_char != old_char:
                char_image = ascii_chars_images[new_char]
                imageReturn.paste(char_image, (x, y))
            x += block_font_size
        y += block_font_size

    old_ascii_art = ascii_art

def image_to_ascii_image(startImage):
    image_to_ascii(startImage)
    ascii_to_image()
    return imageReturn.copy()

# Thread function for capturing and processing frames
def capture_and_process_frames(frame_queue, stop_event, fps_queue):
    while not stop_event.is_set():
        start_time = time.time()

        ret, image = realCam.read()
        if not ret:
            continue
        
        processed_image = image_to_ascii_image(image)
        
        end_time = time.time()
        
        # Put the processed image and time into the queue
        frame_queue.put(processed_image)
        fps_queue.put(end_time - start_time)

# Thread function for displaying frames
def display_frames(frame_queue, cam, stop_event, fps_queue):
    target_size = (cam.width, cam.height)
    fps_times = deque(maxlen=30)  # Store the times of the last 30 frames to calculate FPS
    last_display_time = time.time()
    display_interval = 0.5  # Update FPS display every second

    while not stop_event.is_set():
        if not frame_queue.empty():
            image = frame_queue.get()
            image_np = np.array(image)
            resized_image_np = cv2.resize(image_np, target_size, interpolation=cv2.INTER_NEAREST)
            cam.send(resized_image_np)
            cam.sleep_until_next_frame()

            # Record the frame display time
            if not fps_queue.empty():
                process_time = fps_queue.get()
                fps_times.append(process_time)

            current_time = time.time()
            if current_time - last_display_time >= display_interval:
                if len(fps_times) > 0:
                    avg_frame_time = sum(fps_times) / len(fps_times)
                    fps = 1.0 / avg_frame_time
                else:
                    fps = cam.fps

                # Clear the terminal and display the FPS
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f'FPS: {fps:.2f}')
                print("Frame queue size:", frame_queue.qsize())
                last_display_time = current_time
        else:
            time.sleep(0.01)  # Small sleep to prevent busy waiting


# Créer une webcam virtuelle avec pyvirtualcam
with pyvirtualcam.Camera(width=1280, height=720, fps=60, fmt=PixelFormat.BGR) as cam:
    print(f'Utilisation de la caméra virtuelle : {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')

    setup()

    cam_start_time = time.time()

    # Precompute the target size
    target_size = (cam.width, cam.height)

    # Create queues to hold the frames and processing times
    frame_queue = queue.Queue()
    fps_queue = queue.Queue()

    # Create an event to signal the threads to stop
    stop_event = threading.Event()

    # Create and start the threads
    capture_thread = threading.Thread(target=capture_and_process_frames, args=(frame_queue, stop_event, fps_queue))
    display_thread = threading.Thread(target=display_frames, args=(frame_queue, cam, stop_event, fps_queue))

    capture_thread.start()
    display_thread.start()

    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")

        # Signal the threads to stop
        stop_event.set()

        # Wait for the threads to finish
        capture_thread.join()
        display_thread.join()

        print("Stopped.")
