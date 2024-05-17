from PIL import Image, ImageDraw, ImageFont
import time
import numpy as np


font_size = 20  # Ajuster pour changer la taille de la police
ascii_chars = " .:-=+*#%@8&WM"
ascii_chars_images = []
font_path = "Consolas.ttf"
test_number = 500

# Charger une police de caractères monospacée
font = ImageFont.truetype(font_path, font_size)


start_time = time.time()
# Créer une nouvelle image
image = Image.new('RGB', (font_size*test_number, font_size*test_number), color=(30, 30, 30))
draw = ImageDraw.Draw(image)

for i in range(test_number):
    for j in range(test_number):        
        draw.text((i*font_size, j*font_size), '@', font=font, fill=(250, 250, 250))

end_time = time.time()
print(f"Conversion ASCII en image test 1: {end_time - start_time} secondes")

# Créer une nouvelle image

start_time = time.time()
char_image = Image.new('RGB', (font_size, font_size), color=(30, 30, 30))
char_draw = ImageDraw.Draw(char_image)
char_draw.text((0, 0), '@', font=font, fill=(250, 250, 250))

image2 = Image.new('RGB', (font_size*test_number, font_size*test_number), color=(30, 30, 30))
draw2 = ImageDraw.Draw(image2)

for i in range(test_number):
    for j in range(test_number):        
        image2.paste(char_image, (i * font_size, j * font_size))

end_time = time.time()
print(f"Conversion ASCII en image test 2: {end_time - start_time} secondes")