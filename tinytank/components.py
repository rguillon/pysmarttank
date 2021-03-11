from pysmartnode.components.devices.light import Light
from dev.drivers import BrightnessLightDriver, RgbLightDriver




Light(friendly_name="tiny_tank_white",
      light=BrightnessLightDriver(pin_num=21, is_reverse=False),
      has_brightness=True,
      has_rgb=False)
Light(friendly_name="tiny_tank_red",
      light=BrightnessLightDriver(pin_num=22, is_reverse=False),
      has_brightness=True,
      has_rgb=False)
