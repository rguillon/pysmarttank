from pysmartnode.components.devices.light import Light
from dev.drivers import BrightnessLightDriver, RgbLightDriver




Light(friendly_name="big_tank_cold_white",
      light=BrightnessLightDriver(pin_num=26, is_reverse=False),
      has_brightness=True,
      has_rgb=False)
Light(friendly_name="big_tank_red",
      light=BrightnessLightDriver(pin_num=27, is_reverse=False),
      has_brightness=True,
      has_rgb=False)

