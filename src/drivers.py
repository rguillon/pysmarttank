# Author: Renaud Guillon
# Copyright Renaud Guillon 2021 Released under the MIT license
# Created on 2021-02-19


from machine import Pin, PWM


class BrightnessLightDriver:
    def __init__(self, pin_num, scale= 1023, is_reverse= True):
        self.pwm = PWM(Pin(pin_num))
        self.br = scale
        self._scale = scale
        self._is_rev = is_reverse
        self.off()

    def brightness(self, value):
        self.br = int(value)

    def on(self):
        if self._is_rev:
            self.pwm.duty(self._scale - self.br)
        else:
            self.pwm.duty(self.br)

    def off(self):
        if self._is_rev:
            self.pwm.duty(self._scale)
        else:
            self.pwm.duty(0)

    def scale(self):
        return self._scale


class RgbLightDriver:
    def __init__(self, r_pin_num, g_pin_num, b_pin_num, scale= 1023, is_reverse= True):
        self.r_pwm = PWM(Pin(r_pin_num))
        self.g_pwm = PWM(Pin(g_pin_num))
        self.b_pwm = PWM(Pin(b_pin_num))
        self._scale = scale
        self._is_rev = is_reverse
        self.b = scale
        self.c = {'r': 0, 'g': 0, 'b': 0}

    def scale(self):
        return self._scale

    def on(self):
        self.__update()

    def off(self):
        if self._is_rev:
            self.r_pwm.duty(self._scale)
            self.g_pwm.duty(self._scale)
            self.b_pwm.duty(self._scale)
        else:
            self.r_pwm.duty(0)
            self.g_pwm.duty(0)
            self.b_pwm.duty(0)

    def color(self, value):
        self.c = value
        self.__update()

    def brightness(self, value):
        self.b = value
        self.__update()

    def __update(self):
        if self._is_rev:
            self.r_pwm.duty(self._scale - int(self.b * self.c['r'] / 255))
            self.g_pwm.duty(self._scale - int(self.b * self.c['g'] / 255))
            self.b_pwm.duty(self._scale - int(self.b * self.c['b'] / 255))
        else:
            self.r_pwm.duty(int(self.b * self.c['r'] / 255))
            self.g_pwm.duty(int(self.b * self.c['g'] / 255))
            self.b_pwm.duty(int(self.b * self.c['b'] / 255))
