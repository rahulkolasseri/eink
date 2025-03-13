import esp32, ws2812b, leds
from aspushbutton import Pushbutton
import system, time, asyncio, machine, displayepd
print("main")
ws2812b.off_all()

async def touchs():
    button = Pushbutton(system.TOUCH_BUTTON, suppress=True)

    button.release_func(system.pulseprint, ("SHORT", 80))

    button.double_func(displayepd.display(displayepd.pickbin()))

    button.long_func(system.triple_pulseprint_sleep, ("LONG", 100))

    await asyncio.sleep(5*60*200) 




ws2812b.ease_to(0, (255, 255, 255), 10)
time.sleep(1)






print("running touch test")
asyncio.run(touchs())
print("touch test finished")

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



