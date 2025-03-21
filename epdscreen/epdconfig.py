# /*****************************************************************************
# * | File        :	  epdconfig.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * | This version:   V1.2
# * | Date        :   2022-10-29
# * | Info        :   
# ******************************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
#import logging
import sys
import time
from machine import Pin, SPI  # pylint: disable=C0415

#logger = logging.getLogger(__name__)

class MicroPython:

    def __init__(self):
        # preimport utime
        #import utime  # pylint: disable=C0415, W0611

        self.DC_PIN = self.dc = Pin(40, Pin.OUT)
#        self.dc.mode(Pin.OUT)

        self.CS_PIN = self.cs = Pin(39, Pin.OUT, Pin.PULL_UP)
        # self.cs.mode(Pin.OUT)
        # self.cs.pull(Pin.PULL_UP)

        self.RST_PIN = self.rst = Pin(41, Pin.OUT)
        # self.rst.mode(Pin.OUT)

        self.BUSY_PIN = self.busy = Pin(42, Pin.IN)
        # self.busy.mode(Pin.IN)

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def spi_writebyte(self, data):
        self.spi.write(bytes(c & 0xff for c in data))

    def spi_writebyte2(self, data):
        self.spi.write(bytes(c & 0xff for c in data))

    def spi_writebyte3(self, data):
        # for i in range(len(data)):
        #     self.spi.write(bytes([data[i] & 0xff]))
        #self.spi.write(bytes(c & 0xff for c in data))
        self.spi.write(data)

    def delay_ms(self, delaytime):
        time.sleep_ms(delaytime)

    def module_init(self):
        print("open spi")
        clkpin = Pin(12)
        mosipin = Pin(11)
        self.spi = SPI(1, baudrate=2000000, polarity=0, phase=0, sck = clkpin, mosi = mosipin)
        print("spi opened")
        return 0

    def module_exit(self):
        print("close spi")
        self.spi.deinit()
        print("spi closed")



implementation = MicroPython()



for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))

### END OF FILE ###
