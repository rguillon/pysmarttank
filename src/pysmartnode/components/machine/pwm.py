# Author: Kevin Köck
# Copyright Kevin Köck 2018-2020 Released under the MIT license
# Created on 2018-07-16

"""
example config:
{
    package: .machine.PWM
    component: PWM
    constructor_args: {
        pin: 0              # PWM pin number or PWM object (even Amux pin object)
        #is_reverse : false  # optional, true if the pwm values shall be reversed (for common VCC drivers)
    }
}
Does not publish anything, just unifies writing of esp8266 PWM, esp32, Amux, Arudino, etc
You can pass any PWM object or pin number to PWM() and it will return a corretly subclassed pyPWM object
"""

__version__ = "0.1"
__updated__ = "2021-03-12"

import machine
from sys import platform


class pyPWM:
    """
    Base class to identify all instances of an PWM object sharing the same API
    """

    def __init__(self,  pin, is_reverse=False, safe_value=0):
        self._pin = pin
        self.is_reverse = is_reverse
        if platform == "esp8266" or platform == "esp32":
            self._scale = 1023
        else:
            raise NotImplementedError(
                "Platform {!s} not implemented, please report".format(platform))
        if safe_value is not None:
            self.setDuty(safe_value)

    def setDuty(self, duty: int):
        """
        Set the duty cycle according to used platform.
        :param duty: the new duty cycle
        :return: None
        """
        if self.is_reverse:
            self._pin.duty(int(self._scale - duty))
        else:
            self._pin.duty(int(duty))

    def __str__(self):
        return "pyPWM generic instance"

    __repr__ = __str__

    def scale(self) -> int:
        return self._scale


def PWM(pin,  is_reverse=False, safe_value=0) -> pyPWM:
    if type(pin) == str:
        raise TypeError("PWM pin can't be string")

    return pyPWM(machine.PWM(machine.Pin(pin)), is_reverse=is_reverse, safe_value=0)

