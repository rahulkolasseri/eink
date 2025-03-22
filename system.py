import network, machine, time, esp32, ws2812b, asyncio, leds # type: ignore

############
### WIFI ###
############


def wlansetup():
    wlan = network.WLAN(network.STA_IF)
    return wlan

def readssidpass():
    wificonfig = open("wifis.txt", "r").read().split("\n")
    ssidpass = {}
    for line in wificonfig:
        if line != "":
            ssid, password = line.split("|")
            ssidpass[ssid.strip("\r")] = password.strip("\r")
    return ssidpass

def wlan_on():
    wlan = wlansetup()
    wlan.active(True)

def wlan_off():
    wlan = wlansetup()
    wlan.active(False)

def known_networks():
    wlan = wlansetup()
    wlan_on()
    nets = wlan.scan()
    sorted(nets, key=lambda x: x[3], reverse=True)

    ssidpass = readssidpass()

    return nets, ssidpass

async def aknown_networks():
    leds.wlanled(1)
    wlan = wlansetup()
    wlan_on()
    nets = wlan.scan()
    sorted(nets, key=lambda x: x[3], reverse=True)

    ssidpass = readssidpass()

    return nets, ssidpass

def connect_to_network(nets):
    wlan = wlansetup()
    if not wlan.isconnected() and len(nets) > 0:
        ssid = nets[0][0].decode()
        password = "koala123"
        print(f"connecting to {ssid}")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(0.1)
        print("connected")
        print(wlan.ifconfig())



############
### TIME ###
############

def update_time():
    if wlan.isconnected(): # type: ignore
        import ntptime # type: ignore
        ntptime.settime()
        print(f"time updated, current time is {time.localtime()}")
    else:
        print("not connected to wifi, cannot update time")


############
### BATT ###
############

BATTERY_ADC = machine.Pin(3)


def get_battery_voltage():
    adc_battery = machine.ADC(BATTERY_ADC, atten=machine.ADC.ATTN_11DB)
    val = adc_battery.read_uv() * 2 / 1000000
    return val, adc_battery.read_uv()



# SCREEN_MOSFET = machine.Pin(15, machine.Pin.OUT)
# SCREEN_MOSFET.value(0)

# def screen_on():
#     print("screen on")
#     SCREEN_MOSFET.value(1)

# def screen_off():
#     print("screen off")
#     SCREEN_MOSFET.value(0)

#############
### TOUCH ###
#############

TOUCH_BUTTON = machine.Pin(6, machine.Pin.IN)
from aspushbutton import Pushbutton
# async def touchs():
#     button = Pushbutton(TOUCH_BUTTON, suppress=True)

#     button.release_func(pulseprint, ("SHORT", 80))

#     button.long_func(double_pulseprint, ("LONG", 100))

#     await asyncio.sleep(5*60*200) 



#############
### SLEEP ###
#############

def sleeptime(t=300, wakebutton=TOUCH_BUTTON, forever=False):
    esp32.wake_on_ext0(wakebutton, esp32.WAKEUP_ANY_HIGH)
    ws2812b.ease_to_all_min(20)
    VIBE_MOTOR.value(0)
    wlan_off()
    oledclear(ssd, wri)
    print(f"going to sleep for {t} seconds")
    if forever:
        print("sleeping forever")
        machine.deepsleep()
    else:
        machine.deepsleep(t * 1000)

def sleeptimehours(t=1, wakebutton=TOUCH_BUTTON):
    sleeptime(t * 60 * 60, wakebutton)

def sleeptimeforever(wakebutton=TOUCH_BUTTON):
    sleeptime(300, wakebutton, True)



############
### VIBE ###
############

VIBE_MOTOR = machine.Pin(8, machine.Pin.OUT)
VIBE_MOTOR.value(0)

def pulse_vibe_motor(t=100):
    VIBE_MOTOR.value(1)
    time.sleep_ms(t)
    VIBE_MOTOR.value(0)

def double_pulse_vibe_motor(t=50):
    pulse_vibe_motor(t)
    time.sleep_ms(100)
    pulse_vibe_motor(t)


def triple_pulse_vibe_motor(t=50):
    pulse_vibe_motor(t)
    time.sleep_ms(100)
    pulse_vibe_motor(t)
    time.sleep_ms(100)
    pulse_vibe_motor(t)

def pulseprint(string, t=80):
    print(string)
    pulse_vibe_motor(t)

def double_pulseprint(string, t=100):
    print(string)
    double_pulse_vibe_motor(t)

def triple_pulseprint(string, t=100):
    print(string)
    triple_pulse_vibe_motor(t)

def triple_pulseprint_sleep(string, t=100):
    print(string)
    triple_pulse_vibe_motor(t)
    sleeptimeforever()

############
### OLED ###
############

from oled.ssd1306_setup import WIDTH, HEIGHT, setup
from oled.writer import Writer
import oled.hvnm as hvnm  # Font to use

use_spi=False  # Tested with a 128*64 I2C connected SSD1306 display
ssd = setup(use_spi, soft=True)  # Instantiate display: must inherit from framebuf
ssd.rotate(False)
wri = Writer(ssd, hvnm)
wri.set_textpos(ssd, 0, 0)


def oledprint(str, wri=wri, ssd=ssd):
    wri.printstring(str)
    ssd.show()

def oledclear(ssd=ssd, wri=wri):
    ssd.fill(0)
    wri.set_textpos(ssd, 0, 0)
    ssd.show()