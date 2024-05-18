import cv2
import numpy as np
import os
import time
from PIL import Image, ImageDraw, ImageFont
import pyvirtualcam
from pyvirtualcam import PixelFormat

# Initialisation de la caméra
realCam = cv2.VideoCapture(0)

# Paramètres de l'ASCII art
block_size = 4  # Ajuster pour changer la taille des blocs
font_size = 5  # Ajuster pour changer la taille de la police
ascii_chars = " .':^+*#M%@$"
ascii_chars_images = {}
font_path = "Consolas.ttf"

# Charger une police de caractères monospacée
font = ImageFont.truetype(font_path, font_size)

# Effacer le terminal une seule fois avant la boucle principale
os.system('cls' if os.name == 'nt' else 'clear')

def setup():
    for ascii_char in ascii_chars:
        char_image = Image.new('RGB', (font_size, font_size), color=(30, 30, 30))
        char_draw = ImageDraw.Draw(char_image)
        char_draw.text((0, 0), ascii_char, font=font, fill=(250, 250, 250))
        ascii_chars_images[ascii_char] = char_image


# next steps -> update ascii_art and not recreate it each time, drop \n and use a single string
def image_to_ascii(image):
    # Resize the image using nearest neighbor approach
    small_image = image[::block_size, ::block_size]
    
    # Convert the small image to grayscale
    grayscale_image = np.mean(small_image, axis=2)
    
    # Normalize grayscale image to match the range of ascii_chars
    normalized_image = (grayscale_image / 255 * (len(ascii_chars) - 1)).astype(int)
    
    # Create ASCII art by mapping the normalized image to ascii characters
    ascii_art = "\n".join(
        " ".join(ascii_chars[pixel] for pixel in row)
        for row in normalized_image
    )    
    return ascii_art

# Try updating image and not recreate it for each frame
def ascii_to_image(ascii):
    lines = ascii.split('\n')

    width_obs = max(len(line) for line in lines) * (font_size)
    height_obs = len(lines) * font_size

    # Créer une nouvelle image
    image = Image.new('RGB', (width_obs, height_obs), color=(30, 30, 30))
    draw = ImageDraw.Draw(image)

    # Dessiner le texte ASCII sur l'image

    y = 0
    for line in lines:
        x = 0
        for char in line:
            char_image = ascii_chars_images[char]
            image.paste(char_image, (x, y))
            x += font_size
        y += font_size

    return image


def image_to_ascii_image(startImage):
    #start_time = time.time()
    ascii = image_to_ascii(startImage)
    #end_time = time.time()
    #print(f"    Temps de conversion en ASCII: {end_time - start_time:.8f}")

    #start_time = time.time()
    image = ascii_to_image(ascii)
    #end_time = time.time()
    #print(f"    Temps de conversion en image: {end_time - start_time:.8f}")
    return image

# Créer une webcam virtuelle avec pyvirtualcam
with pyvirtualcam.Camera(width=2560, height=1940, fps=20, fmt=PixelFormat.BGR) as cam:
    print(f'Utilisation de la caméra virtuelle : {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')

    setup()

    while True:
        start_total_time = time.time()

        ret, image = realCam.read()
        if not ret:
            break

        #start_time = time.time()
        new_image = image_to_ascii_image(image)
        #end_time = time.time()
        #print(f"Temps de traitement: {end_time - start_time:.8f}")

        #start_time = time.time()
        new_image = new_image.resize((2560, 1940), Image.NEAREST)
        #end_time = time.time()
        #print(f"Temps de redimensionnement: {end_time - start_time:.8f}")

        #start_time = time.time()
        image_np = np.array(new_image)
        #end_time = time.time()
        #print(f"Temps de conversion: {end_time - start_time:.8f}")

        #start_time = time.time()
        cam.send(image_np)
        #end_time = time.time()
        #print(f"Temps d'envoi: {end_time - start_time:.8f}")

        cam.sleep_until_next_frame()

        end_total_time = time.time()
        
        os.system('cls' if os.name == 'nt' else 'clear')
        #print(f"Total: {end_total_time - start_total_time:.8f}")
        print(f"FPS: {1 / (end_total_time - start_total_time):.2f}")
        #print()
