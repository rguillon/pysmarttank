'''
Created on 01.06.2018

@author: Kevin Köck
'''

__version__ = "2.0"
__updated__ = "2019-10-20"

import gc

from machine import Pin, PWM

from pysmartnode import config

gc.collect()  # It's important to call gc.collect() to keep the RAM fragmentation to a minimum

from pysmartnode.components.devices.light import Light

gc.collect()


class BrightnessLightDriver:
    def __init__(self, pin_num):
        self.pwm = PWM(Pin(pin_num))
        self.br = 0
        self._scale = 1023
        self.off()

    def brightness(self, value):
        print("LIGHT BRIGHTNESS {}".format(value))
        self.br = value
        self.pwm.duty(self._scale - int(value))

    def on(self):
        print("LIGHT ON")
        self.pwm.duty(0)

    def off(self):
        print("LIGHT OFF")
        self.pwm.duty(self._scale)

    def scale(self):
        return self._scale


class RgbLightDriver:
    def __init__(self, r_pin_num, g_pin_num, b_pin_num):
        self.r_pwm = PWM(Pin(r_pin_num))
        self.g_pwm = PWM(Pin(g_pin_num))
        self.b_pwm = PWM(Pin(b_pin_num))
        self._scale = 1023
        self.b = 0
        self.c = {'r': 0, 'g': 0, 'b': 0}

    def scale(self):
        return self._scale

    def on(self):
        self.__update()

    def off(self):
        self.r_pwm.duty(self._scale)
        self.g_pwm.duty(self._scale)
        self.b_pwm.duty(self._scale)

    def color(self, value):
        self.c = value
        self.__update()

    def brightness(self, value):
        self.b = value
        self.__update()

    def __update(self):
        self.r_pwm.duty(int(1023 - int(self.b * self.c['r'] / 255)))
        self.g_pwm.duty(int(1023 - int(self.b * self.c['g'] / 255)))
        self.b_pwm.duty(int(1023 - int(self.b * self.c['b'] / 255)))


config.addComponent("test_light", Light(friendly_name="test_light", light=BrightnessLightDriver(17)))

config.addComponent("test_rgb_light", Light(friendly_name="test_rgb_light", light=RgbLightDriver(14, 15, 26)))
