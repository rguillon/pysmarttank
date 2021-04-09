from pysmartnode.components.devices.light import Light
from pysmartnode.components.machine.pwm import PWM
from pysmartnode.components.machine.soft_reset import SoftReset


Light(friendly_name='tiny_tank_cold_white',
      light1=PWM(pin=18),
      has_brightness=True,
      has_rgb=False)

Light(friendly_name='tiny_tank_red',
      light1=PWM(pin=19),
      has_brightness=True,
      has_rgb=False)

Light(friendly_name='tiny_tank_rgb',
      light1=PWM(pin=21),
      lightG=PWM(pin=22),
      lightB=PWM(pin=23),
      has_brightness=True,
      has_rgb=True)

SoftReset(friendly_name="tiny_tank_reset")
