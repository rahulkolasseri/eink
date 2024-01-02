import time, machine, neopixel, random, easing_functions, math
pin = machine.Pin(18, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, 3)

def off_all():
    print("off all")
    for i in range(3):
        np[i] = (0, 0, 0)
    np.write()

def on_all():
    print("on all")
    for i in range(3):
        np[i] = (255, 255, 255)
    np.write()

def red(led):
    print(f"red {led}")
    np[led] = (255, 0, 0)
    np.write()

def green(led):
    print(f"green {led}")
    np[led] = (0, 255, 0)
    np.write()

def blue(led):
    print(f"blue {led}")
    np[led] = (0, 0, 255)
    np.write()

def red_all():
    print("red all")
    for i in range(3):
        np[i] = (255, 0, 0)
    np.write()

def green_all():
    print("green all")
    for i in range(3):
        np[i] = (0, 255, 0)
    np.write()

def blue_all():
    print("blue all")
    for i in range(3):
        np[i] = (0, 0, 255)
    np.write()

def push():
    print("push")
    temp = np[2]
    np[2] = np[1]
    np[1] = np[0]
    np[0] = temp
    np.write()


def transit_path(c1, c2, steps=10):
    c1g, c1r, c1b = c1
    c2g, c2r, c2b = c2

    ease_r = easing_functions.CubicEaseInOut(start=c1r, end=c2r, duration=steps)
    ease_g = easing_functions.CubicEaseInOut(start=c1g, end=c2g, duration=steps)
    ease_b = easing_functions.CubicEaseInOut(start=c1b, end=c2b, duration=steps)

    c_steps = []

    for i in range(steps):
        r = math.floor(ease_r.ease(i))
        g = math.floor(ease_g.ease(i))
        b = math.floor(ease_b.ease(i))
        if r > 255:
            r = 255
        if g > 255:
            g = 255
        if b > 255:
            b = 255
        c_steps.append((g, r, b))

    return c_steps

def ease_to(led, c2, steps=10):
    c1 = np[led]
    c_steps = transit_path(c1, c2, steps)
    for c in c_steps:
        np[led] = c
        np.write()
        time.sleep(0.1)

def ease_to_all(c2, steps=10):
    l1c1 = np[0]
    l2c1 = np[1]
    l3c1 = np[2]
    l1c_steps = transit_path(l1c1, c2, steps)
    l2c_steps = transit_path(l2c1, c2, steps)
    l3c_steps = transit_path(l3c1, c2, steps)
    for i in range(steps):
        np[0] = l1c_steps[i]
        np[1] = l2c_steps[i]
        np[2] = l3c_steps[i]
        np.write()
        time.sleep(0.1)

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def ease_to_random(led, steps=10):
    c2 = random_color()
    ease_to(led, c2, steps)

def ease_to_random_all(steps=10, same=True):
    if same:
        c2 = random_color()
        ease_to_all(c2, steps)
    else:
        l1c2 = random_color()
        l2c2 = random_color()
        l3c2 = random_color()
        l1c_steps = transit_path(np[0], l1c2, steps)
        l2c_steps = transit_path(np[1], l2c2, steps)
        l3c_steps = transit_path(np[2], l3c2, steps)
        for i in range(steps):
            np[0] = l1c_steps[i]
            np[1] = l2c_steps[i]
            np[2] = l3c_steps[i]
            np.write()
            time.sleep(0.1)

def breath(led, repeats=3, steps=7):
    for i in range(repeats):
        c1 = np[led]
        c2 = (0, 0, 0)
        c_steps = transit_path(c1, c2, steps)
        for c in c_steps:
            np[led] = c
            np.write()
            time.sleep(0.1)
        for c in c_steps[::-1]:
            np[led] = c
            np.write()
            time.sleep(0.1)