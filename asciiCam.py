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
block_size = 5  # Ajuster pour changer la taille des blocs
font_size = 20  # Ajuster pour changer la taille de la police
ascii_chars = " .:-=+*#%@8&WM"

font = "DejaVuSansMono.ttf"

# Effacer le terminal une seule fois avant la boucle principale
os.system('cls' if os.name == 'nt' else 'clear')

# Fonction pour convertir l'ASCII art en image
def ascii_to_image(ascii_str, font_path, font_size=12):
    lines = ascii_str.split('\n')

    width_obs = max(len(line) for line in lines) * (font_size // 2)
    height_obs = len(lines) * font_size

    # Créer une nouvelle image
    image = Image.new('RGB', (width_obs, height_obs), color=(30, 30, 30))
    draw = ImageDraw.Draw(image)

    # Charger une police de caractères monospacée
    font = ImageFont.truetype(font_path, font_size)

    # Dessiner le texte ASCII sur l'image
    y = 0
    for line in lines:
        draw.text((0, y), line, font=font, fill=(250, 250, 250))
        y += font_size

    return image

def image_to_ascii(image, block_size=6, ascii_chars=" .:-=+*#%@8&WM"):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    h, w = image.shape
    new_h = h // block_size
    new_w = w // block_size
    
    ascii_art = ""
    
    for i in range(new_h):
        ascii_row = ""
        for j in range(new_w):
            block = image[i * block_size:(i + 1) * block_size, j * block_size:(j + 1) * block_size]
            avg_intensity = np.mean(block)
            char_index = int((avg_intensity / 255) * (len(ascii_chars) - 1))
            ascii_row += ascii_chars[char_index] + " "
        ascii_art += ascii_row + "\n"
    return ascii_art

# Créer une webcam virtuelle avec pyvirtualcam
with pyvirtualcam.Camera(width=2560, height=1940, fps=30, fmt=PixelFormat.BGR) as cam:
    print(f'Utilisation de la caméra virtuelle : {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')

    while True:
        start_time = time.time()

        ret, image = realCam.read()
        if not ret:
            break
        
        ascii_art = image_to_ascii(image, block_size, ascii_chars)
        
        # Convertir l'ASCII art en image
        new_image = ascii_to_image(ascii_art, font_path=font, font_size=font_size)
        
        # Redimensionner l'image pour correspondre à la résolution attendue par la caméra virtuelle
        new_image = new_image.resize((2560, 1940), Image.NEAREST)
        
        # Convertir l'image PIL en tableau NumPy
        image_np = np.array(new_image)
        
        # Envoyer l'image à la webcam virtuelle
        cam.send(image_np)
        
        # Simuler un délai pour maintenir le FPS
        cam.sleep_until_next_frame()

        end_time = time.time()
        fps = 1 / (end_time - start_time)

        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"FPS: {fps:.2f}")

        # Pour arrêter le script, vous pouvez utiliser une condition ou une interruption clavier (Ctrl+C)
