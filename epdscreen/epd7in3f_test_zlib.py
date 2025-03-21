#import sys
#import os
import epd7in3f
import time, os, micropython, zlib, gc
#import logging

# logger = logging.getLogger(__name__)

print("epd7in3f Demo")

epd = epd7in3f.EPD()

files = os.listdir()
zlibs = [zlib for zlib in files if zlib.endswith(".zlib")]
print(zlibs)

if len(zlibs) > 0 and type(zlibs) == list:
    for zlib in zlibs:
        print("init and Clear")
        print("init")
        epd.init()
        time.sleep(1)
        epd.Clear()
        print("Cleared")
        print(micropython.mem_info())
        print(f"Loading {zlib}")
        with open(zlib, "rb") as z:
            with zlib.DecompIO(z.read(), wbits=9).read() as image:
                print("Image loaded")
                print(micropython.mem_info())
                for i in range(10):
                    print(f"Displaying image in {10-i} seconds")
                    time.sleep(1)
                epd.display(image)
                print("Image displayed")
        print(micropython.mem_info())
        print("freeing memory")
        gc.collect()
        print(micropython.mem_info())
        print("Sleeping for 60 seconds")
        epd.sleep()
        print("Sleep started")
        time.sleep(60)
        print("Waking")
else:
    print("No .zlib files found")

print("Done")