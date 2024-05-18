import cv2
import numpy as np
import os
import time
from PIL import Image, ImageDraw, ImageFont
import pyvirtualcam
from pyvirtualcam import PixelFormat
import concurrent.futures
from colorama import Fore, Back, Style, init

font_size = 20  # Ajuster pour changer la taille de la police
ascii_chars = " .:-=+*#%@8&WM"
ascii_chars_images = {}
font_path = "Consolas.ttf"

num_threads = 10

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
    
setup()

print(ascii_chars_images)

# créer une image qui contient toute les images des caractères
image = Image.new('RGB', (font_size * len(ascii_chars), font_size), color=(30, 30, 30))
x = 0
for ascii_char, char_image in ascii_chars_images.items():
    image.paste(char_image, (x, 0))
    x += font_size

image.show()
