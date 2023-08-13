"""
github.com/n0nexist/mcImager
Minecraft image to schematic converter
"""

from PIL import Image
import colorsys
import mcschematic
import os
import time
from colorama import Fore, Style, init
import concurrent.futures

init()

print(f"""{Fore.GREEN}{Style.BRIGHT}
           _____                       
 _____ ___|     |_____ ___ ___ ___ ___ 
|     |  _|-   -|     | .'| . | -_|  _|
|_|_|_|___|_____|_|_|_|__,|_  |___|_|  
                          |___|        
{Style.RESET_ALL}{Fore.WHITE}{Style.DIM} minecraft image to schematic converter{Style.RESET_ALL}
""")

schem = mcschematic.MCSchematic()
schematic_version = mcschematic.Version.JE_1_20_1

# Definizione della mappa dei blocchi e dei loro colori
concrete_colors = {
    "white_concrete": [(255, 255, 255), (250, 250, 250), (240, 240, 240), (230, 230, 230), (220, 220, 220)],
    "orange_concrete": [(223, 108, 20), (215, 100, 15), (205, 90, 10), (200, 85, 10), (195, 80, 10)],
    "magenta_concrete": [(179, 80, 188), (170, 75, 175), (160, 70, 165), (155, 65, 160), (150, 60, 155)],
    "light_blue_concrete": [(103, 137, 211), (95, 125, 200), (85, 115, 190), (80, 110, 185), (75, 105, 180)],
    "yellow_concrete": [(217, 228, 40), (210, 220, 35), (205, 215, 30), (200, 210, 25), (195, 200, 20)],
    "lime_concrete": [(27, 165, 40), (30, 160, 35), (35, 155, 30), (40, 150, 25), (45, 145, 20)],
    "pink_concrete": [(207, 96, 144), (200, 90, 135), (195, 85, 130), (190, 80, 125), (185, 75, 120)],
    "gray_concrete": [(64, 64, 64), (60, 60, 60), (55, 55, 55), (50, 50, 50), (45, 45, 45)],
    "light_gray_concrete": [(154, 161, 161), (150, 155, 155), (145, 150, 150), (140, 145, 145), (135, 140, 140)],
    "cyan_concrete": [(40, 118, 151), (35, 115, 145), (30, 110, 140), (25, 105, 135), (20, 100, 130)],
    "purple_concrete": [(127, 63, 178), (120, 60, 170), (115, 55, 165), (110, 50, 160), (105, 45, 155)],
    "blue_concrete": [(46, 57, 142), (40, 50, 130), (35, 45, 125), (30, 40, 120), (25, 35, 115)],
    "brown_concrete": [(79, 50, 31), (75, 45, 28), (70, 45, 25), (65, 40, 22), (60, 40, 20)],
    "green_concrete": [(53, 70, 27), (50, 65, 25), (45, 60, 22), (40, 55, 20), (35, 50, 18)],
    "red_concrete": [(150, 52, 48), (145, 50, 45), (140, 45, 42), (135, 42, 40), (130, 40, 37)],
    "black_concrete": [(27, 27, 27), (25, 25, 25), (20, 20, 20), (15, 15, 15), (10, 10, 10)],
}

# Prendi il colore più vicino a quello inserito
def calculate_distance(target_color, color):
    distance = sum((a - b) ** 2 for a, b in zip(target_color, color))
    return distance

def closest_color(target_color, color_list):
    min_distance = float("inf")
    closest_color = None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_color = {executor.submit(calculate_distance, target_color, color[1][0]): color for color in color_list.items()}
        for future in concurrent.futures.as_completed(future_to_color):
            color = future_to_color[future]
            distance = future.result()
            if distance < min_distance:
                min_distance = distance
                closest_color = color[0]

    return closest_color

# Ridimensiona l'immagine
def resize_image(path, width, height):
    try:
        image = Image.open(path)
        resized_image = image.resize((width, height), Image.ANTIALIAS)
        resized_image.save(f"{path}_TEMPCOPY.png")
    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}Exception while resizing image: {Style.RESET_ALL}{e}")
        exit(1)

# Carica l'immagine
img = input(f"{Style.BRIGHT}Image path {Fore.GREEN}[{Fore.RESET}without .png at the end{Fore.GREEN}]{Fore.RESET}:{Fore.CYAN} ")+".png"
choice = input(f"{Fore.RESET}Do you want to resize the image? {Fore.GREEN}[{Fore.RESET}y{Fore.CYAN}/{Fore.RESET}n{Fore.GREEN}]{Fore.RESET}:{Fore.CYAN} ")

if choice.lower() == "y":
    width = input(f"{Fore.RESET}Width:{Fore.CYAN} ")
    height = input(f"{Fore.RESET}Height: {Fore.CYAN}")
    print(f"{Fore.RESET}{Style.DIM}Resizing image..")
    resize_image(img,int(width),int(height))

    image = Image.open(f"{img}_TEMPCOPY.png")
    pixels = image.load()

else:
    image = Image.open(img)
    pixels = image.load()

# Dimensioni dell'immagine
width, height = image.size

# Calcola il numero delle iterazioni totali
totIterations = width*height

# Crea la matrice di output
output_matrix = []

# Cicla attraverso i pixel e aggiungi ciascun blocco alla matrice
a = 0
for y in range(height):
    row_blocks = []
    for x in range(width):
        a += 1
        pixel_color = pixels[x, y]
        pixel_color_rgb = pixel_color[:3]  # Considera solo RGB
        closest_block = closest_color(pixel_color_rgb, concrete_colors)
        print(f"{Style.DIM}Generating matrix.. {Fore.GREEN}[{Style.RESET_ALL}{Style.BRIGHT}{a}{Style.RESET_ALL}{Fore.CYAN}/{Fore.RESET}{Style.BRIGHT}{totIterations}{Fore.GREEN}]{Style.RESET_ALL}",end="\r")
        row_blocks.append(closest_block)
    output_matrix.append(row_blocks)

# Metti la matrice dentro una schematica
print("\n",end="\r")
c = 0
r = 0
a = 0
for row in output_matrix:
    c = 0
    for column in row:
        a += 1
        schem.setBlock((c, -r, 0), f"minecraft:{column}") # Metti il blocco dentro la schematica
        print(f"{Style.DIM}Dumping matrix inside of a schematic.. {Fore.GREEN}[{Style.RESET_ALL}{Style.BRIGHT}{a}{Style.RESET_ALL}{Fore.CYAN}/{Fore.RESET}{Style.BRIGHT}{totIterations}{Fore.GREEN}]{Style.RESET_ALL}",end="\r")
        c += 1
    r += 1

# Rimuovi l'immagine temporanea (se esiste)
if choice.lower() == "y":
    os.remove(f"{img}_TEMPCOPY.png")

# Salva la schematica
schem.save( ".", input(f"\n{Style.RESET_ALL}{Style.BRIGHT}Save as:{Fore.CYAN} "), schematic_version)

# Esci dal programma
print(f"{Style.DIM}{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
exit(0)