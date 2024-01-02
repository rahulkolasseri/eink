import network, machine, time
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

BATTERY_ADC = machine.Pin(3)


def get_battery_voltage():
    adc_battery = machine.ADC(BATTERY_ADC, atten=machine.ADC.ATTN_11DB)
    val = adc_battery.read_uv() * 2 / 1000000
    return val, adc_battery.read_uv()
