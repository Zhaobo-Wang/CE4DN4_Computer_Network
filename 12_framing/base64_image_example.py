#!/usr/bin/env python3

########################################################################

import base64

########################################################################

# Original image
INPUT_FILE = "./image.jpg"

# Base64 encoded version
OUTPUT_FILE = INPUT_FILE + ".base64"

# Reconstructed image
RECONSTRUCTED_FILE = OUTPUT_FILE + ".jpg"

# Open the image and do the base64 encoding.
with open(INPUT_FILE, "br") as file:
    file_base64 = base64.b64encode(file.read())

# print(file_base64)

# Write the encoded image to a file.
with open(OUTPUT_FILE, "+wb") as file:
    file.write(file_base64)

# Read the base64 encoded image and decode it.    
with open(OUTPUT_FILE, "r") as file:
    file_decoded = base64.b64decode(file.read())

# Recover the original file and write it.    
with open(RECONSTRUCTED_FILE, "+wb") as file:
    file.write(file_decoded)




