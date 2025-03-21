import system
system.oledprint("Hello")

import esp32, ws2812b, leds # type: ignore
import epdscreen.displayepd as displayepd
import time, asyncio, machine # type: ignore
import oled.menu as menu

asyncio.run(menu.menuStart())















