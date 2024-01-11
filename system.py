import network, machine, time, esp32
wlan = network.WLAN(network.STA_IF)

def wlan_on():
    wlan.active(True)

def wlan_off():
    wlan.active(False)

def known_networks():
    wlan_on()
    nets = wlan.scan()
    known = []
    for net in nets:
        ssid = net[0].decode()
        if "anitha" in ssid.lower():
            known.append(net)
    sorted(known, key=lambda x: x[3], reverse=True)
    return known

def connect_to_network(nets):
    if not wlan.isconnected() and len(nets) > 0:
        ssid = nets[0][0].decode()
        password = "koala123"
        print(f"connecting to {ssid}")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(0.1)
        print("connected")
        print(wlan.ifconfig())

def update_time():
    if wlan.isconnected():
        import ntptime
        ntptime.settime()
        print(f"time updated, current time is {time.localtime()}")
    else:
        print("not connected to wifi, cannot update time")


BATTERY_ADC = machine.Pin(3)


def get_battery_voltage():
    adc_battery = machine.ADC(BATTERY_ADC, atten=machine.ADC.ATTN_11DB)
    val = adc_battery.read_uv() * 2 / 1000000
    return val, adc_battery.read_uv()

SCREEN_MOSFET = machine.Pin(15, machine.Pin.OUT)
SCREEN_MOSFET.value(0)

def screen_on():
    print("screen on")
    SCREEN_MOSFET.value(1)

def screen_off():
    print("screen off")
    SCREEN_MOSFET.value(0)

TOUCH_BUTTON = machine.Pin(6, machine.Pin.IN)

VIBE_MOTOR = machine.Pin(8, machine.Pin.OUT)
VIBE_MOTOR.value(0)

def pulse_vibe_motor(t=100):
    VIBE_MOTOR.value(1)
    time.sleep_ms(t)
    VIBE_MOTOR.value(0)

def triple_pulse_vibe_motor(t=50):
    pulse_vibe_motor(t)
    time.sleep_ms(100)
    pulse_vibe_motor(t)
    time.sleep_ms(100)
    pulse_vibe_motor(t)

def pulseprint(string, t=80):
    print(string)
    pulse_vibe_motor(t)

def triple_pulseprint(string, t=100):
    print(string)
    triple_pulse_vibe_motor(t)

def sleeptime(t=300, wakebutton=TOUCH_BUTTON):
    esp32.wake_on_ext0(wakebutton, esp32.WAKEUP_ANY_HIGH)
    print(f"going to sleep for {t} seconds")
    machine.deepsleep(t * 1000)