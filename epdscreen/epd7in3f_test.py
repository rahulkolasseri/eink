#import sys
#import os
import epd7in3f
import time
#import logging

# logger = logging.getLogger(__name__)

print("epd7in3f Demo")

epd = epd7in3f.EPD()
print("init and Clear")
epd.init()
epd.Clear()
print("Cleared")
print("Loading image")

with open("image.bin", "rb") as f:
    image = f.read()


print("Image loaded")
for i in range(10):
    print(f"Displaying image in {10-i} seconds")
    time.sleep(1)
epd.display(image)
print("Image displayed")
time.sleep(3)
print("Sleeping")
epd.sleep()
time.sleep(3)
print("Waking")