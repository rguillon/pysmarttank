from pysmartnode.components.devices.light import Light
from drivers import BrightnessLightDriver, RgbLightDriver




Light(friendly_name="test_light_01",
      light=BrightnessLightDriver(19),
      has_brightness=True,
      has_rgb=False)
Light(friendly_name="test_light_02",
      light=BrightnessLightDriver(18),
      has_brightness=True,
      has_rgb=False)

Light(friendly_name="test_rgb_light_03",
      light=RgbLightDriver(23, 22, 21),
      has_brightness=True,
      has_rgb=True)
