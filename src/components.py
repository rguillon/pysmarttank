from pysmartnode.components.devices.light import Light
from drivers import BrightnessLightDriver, RgbLightDriver




Light(friendly_name="test_light", light=BrightnessLightDriver(17))

Light(friendly_name="test_rgb_light", light=RgbLightDriver(14, 15, 16))
