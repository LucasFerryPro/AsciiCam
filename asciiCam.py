import cv2
import numpy as np
import os
import concurrent.futures

cam = cv2.VideoCapture(0)

block_size = 5

ascii_chars = " .:-=+*#%@8&WM"

def segment_to_ascii(segment, block_size, ascii_chars, index):
    h, w = segment.shape
    ascii_row = ""
    for i in range(0, h, block_size):
        for j in range(0, w, block_size):
            block = segment[i:i + block_size, j:j + block_size]
            avg_intensity = np.mean(block)
            char_index = int(avg_intensity / 255 * (len(ascii_chars) - 1))
            ascii_row += ascii_chars[char_index] + "  "
        ascii_row += "\n"
    return index, ascii_row

def process_image_in_parallel(image, block_size, ascii_chars, num_threads=20):
    h, w = image.shape
    segment_height = h // num_threads
    segments = [(image[i*segment_height:(i+1)*segment_height, :], block_size, ascii_chars, i) for i in range(num_threads)]

    ascii_image_parts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(segment_to_ascii, *segment) for segment in segments]
        for future in concurrent.futures.as_completed(futures):
            ascii_image_parts.append(future.result())

    # Trier les parties par index pour maintenir l'ordre
    ascii_image_parts.sort(key=lambda x: x[0])
    ascii_image = "".join([part[1] for part in ascii_image_parts])
    return ascii_image

# Effacer le terminal une seule fois avant la boucle principale
os.system('cls' if os.name == 'nt' else 'clear')

while True:
    ret, image = cam.read()
    if not ret:
        break

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    ascii_image = process_image_in_parallel(image, block_size, ascii_chars)

    # Effacer le terminal et afficher l'image d'ASCII art
    os.system('cls' if os.name == 'nt' else 'clear')
    print(ascii_image, end="")
