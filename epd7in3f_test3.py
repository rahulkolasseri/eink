#import sys
#import os
import epd7in3f
import time, os, micropython
#import logging

# logger = logging.getLogger(__name__)

print("epd7in3f Demo")

epd = epd7in3f.EPD()

files = os.listdir()
bins = [bin for bin in files if bin.endswith(".bin")]
print(bins)

if len(bins) > 0 and type(bins) == list:
    for bin in bins:
        print("init and Clear")
        print("init")
        epd.init()
        time.sleep(1)
        epd.Clear()
        print("Cleared")
        print(micropython.mem_info())
        print(f"Loading {bin}")
        with open(bin, "rb") as f:
            image = f.read()
        print("Image loaded")
        print(micropython.mem_info())
        for i in range(10):
            print(f"Displaying image in {10-i} seconds")
            time.sleep(1)
        epd.display(image)
        print("Image displayed")
        time.sleep(3)
        print("Sleeping for 60 seconds")
        epd.sleep()
        time.sleep(60)
        print("Waking")
else:
    print("No .bin files found")

print("Done")