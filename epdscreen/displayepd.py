import system
import epdscreen.epd7in3f as epd7in3f
import time, os, micropython, random, ws2812b # type: ignore

epd = epd7in3f.EPD()



def pickbin():
    files = os.listdir()
    bins = [bin for bin in files if bin.endswith(".bin")]
    print(bins)
    if len(bins) > 0 and type(bins) == list:
        return random.choice(bins)
    else:
        return None




def display(bin):
    print("init and Clear")
    print("init")
    epd.init()
    time.sleep(1)
    ws2812b.ease_to(1, (0, 0, 255), 10)
    epd.Clear()
    print("Cleared")
    print(micropython.mem_info())
    print(f"Loading {bin}")
    with open(bin, "rb") as f:
        image = f.read()
    print("Image loaded")
    print(micropython.mem_info())
    for i in range(2):
        print(f"Displaying image in {10-i} seconds")
        time.sleep(1)
    ws2812b.ease_to(1, (0, 255, 0), 10)
    epd.display(image)
    print("Image displayed")
    time.sleep(3)
    ws2812b.ease_to(1, (0, 0, 0), 10)
    print("Sleeping for 60 seconds")
    epd.sleep()