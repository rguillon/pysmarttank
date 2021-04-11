from pysmartnode.components.devices.light import Light
from pysmartnode.components.machine.pwm import PWM
from pysmartnode.components.machine.soft_reset import SoftReset
from pysmartnode.components.devices.ha_status_updater import HaStatusUpdater

# PWM objects will set the output to a safe value when created, create them all
# before the Compoments reduces the time where the output have random values
pwm_18 = PWM(pin=18)
pwm_19 = PWM(pin=19)

pwm_21 = PWM(pin=21)
pwm_22 = PWM(pin=22)
pwm_23 = PWM(pin=23)

Light(friendly_name='big_tank_cold_white',
      light1=pwm_18,
      has_brightness=True,
      has_rgb=False)

Light(friendly_name='big_tank_red',
      light1=pwm_19,
      has_brightness=True,
      has_rgb=False)

Light(friendly_name='big_tank_rgb',
      light1=pwm_21,
      lightG=pwm_22,
      lightB=pwm_23,
      has_brightness=True,
      has_rgb=True)

SoftReset(friendly_name="Big Tank reset")

HaStatusUpdater()
