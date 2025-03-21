#import ws2812b_basic as ws2812b
# import wifi
# from microdot.microdot import Microdot, Response

# wifi.connect()

# app = Microdot()

# @app.route('/')
# def index(request):
#     try:
#         with open('webpage/index.html', 'r') as f:
#             html = f.read()
#         return Response(body=html, headers={'Content-Type': 'text/html'})
#     except Exception as e:
#         return Response(body=f"Error: {str(e)}", status_code=500)

# @app.route('/toggle', methods=['POST'])
# def toggle(request):
#     ws2812b.flip()
#     state = "on" if ws2812b.isOn() else "off"
#     return Response(body=f'{{"state": "{state}"}}', headers={'Content-Type': 'application/json'})

# @app.route('/state')
# def get_state(request):
#     state = "on" if ws2812b.isOn() else "off"
#     return Response(body=f'{{"state": "{state}"}}', headers={'Content-Type': 'application/json'})

# print("Starting web server...")
# app.run(port=80, debug=True)

from machine import Pin, I2C
import time

from ssd1306_setup import WIDTH, HEIGHT, setup
from writer import Writer
import hvnm  # Font to use

use_spi=False  # Tested with a 128*64 I2C connected SSD1306 display
ssd = setup(use_spi, soft=True)  # Instantiate display: must inherit from framebuf
ssd.rotate(False)
wri = Writer(ssd, hvnm)
wri.set_textpos(ssd, 0, 0)


def pprint(str, wri=wri, ssd=ssd):
    wri.printstring(str)
    ssd.show()

def clear(ssd, wri):
    ssd.fill(0)
    wri.set_textpos(ssd, 0, 0)
    ssd.show()
    
    
pprint("hellooooooooooooooooooo")
time.sleep(2)
pprint("\nworld")


# if machine.reset_cause() == machine.DEEPSLEEP_RESET and machine.wake_reason() == 2:
#     print("woke from a deep sleep by pin")
#     system.blink([0,1,2], (0,0,255), 0.15, 0.1, 3, (0,0,0), True)
# elif machine.reset_cause() == machine.HARD_RESET:
#     print("woke from a hard reset")
# elif machine.reset_cause() == machine.SOFT_RESET:
#     print("woke from a soft reset")
# elif machine.reset_cause() == machine.WDT_RESET:
#     print("woke from a watchdog reset")
# else:
#     print(f"woke from a {machine.reset_cause()} reset")

# time.sleep(2)



# ws2812b.red_all()
# time.sleep(2)
# ws2812b.ease_to_all_min(20)
# system.sleeptime(300)