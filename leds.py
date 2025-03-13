import ws2812b

def powerled(state):
    if state == 0:
        ws2812b.off(0)
    elif state == 1:
        ws2812b.green(0)
    elif state == 2:
        ws2812b.blue(0)
    elif state == 3:
        ws2812b.red(0)

