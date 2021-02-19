# Author: Renaud Guillon
# Copyright Kevin Köck 2018-2020 Released under the MIT license
# Created on 2018-06-22

"""
example config for MyComponent:
{
    package: <package_path>
    component: MyComponent
    constructor_args: {
        my_value: "hi there"             
        # mqtt_topic: sometopic  # optional, defaults to home/<controller-id>/<component_name>/<component-count>/set
        # mqtt_topic2: sometopic # optional, defautls to home/sometopic
        # friendly_name: null    # optional, friendly name shown in homeassistant gui with mqtt discovery
        # discover: true         # optional, if false no discovery message for homeassistant will be sent.
    }
}l
"""

__updated__ = "2020-03-29"
__version__ = "1.91"

import gc
import time

import uasyncio as asyncio
from pysmartnode import config
from pysmartnode import logging
from pysmartnode.utils.component import ComponentBase, DISCOVERY_SWITCH

####################
# choose a component name that will be used for logging (not in leightweight_log),
# a default mqtt topic that can be changed by received or local component configuration
# as well as for the component name in homeassistant.
COMPONENT_NAME = "Light"
# define the type of the component according to the homeassistant specifications
_COMPONENT_TYPE = "light"
####################

_log = logging.getLogger(COMPONENT_NAME)
_mqtt = config.getMQTT()
gc.collect()
import json

_unit_index = -1


class Light(ComponentBase):
    def __init__(self, friendly_name=None, discover=True, light=None, has_brightness=True, has_rgb=True, **kwargs):
        global _unit_index
        _unit_index += 1
        super().__init__(COMPONENT_NAME, __version__, _unit_index, discover=discover, **kwargs)

        self._command_topic = _mqtt.getDeviceTopic(
            "{!s}{!s}".format(COMPONENT_NAME, self._count), is_request=True)
        _mqtt.subscribeSync(self._command_topic, self.on_set, self, check_retained_state=True)

        self._frn = friendly_name  # will default to unique name in discovery if None

        self._light = light
        self.states = {'state': 'OFF'}
        self._has_brightness = has_brightness
        if self._has_brightness:
            self.states['brightness'] = 0
        self._has_rgb = has_rgb
        if self._has_rgb:
            self.states['rgb'] = {'r':0, 'g':0, 'b':0}


        self.is_updated = False

        self._loop_task = asyncio.create_task(self._loop())
        gc.collect()

    async def _init_network(self):
        await super()._init_network()

    async def _loop(self):
        while True:
            await asyncio.sleep(1)
            if self.is_updated:
                await _mqtt.publish(self._command_topic[:-4], json.dumps(self.states), qos=1)
                self.is_updated = False

    async def _remove(self):
        """Will be called if the component gets removed"""
        # Cancel any loops/asyncio coroutines started by the component
        if self._loop_task is not None:
            self._loop_task.cancel()
        await super()._remove()

    async def _discovery(self, register=True):
        """
        Send discovery messages
        :param register: if True send discovery message, if False send empty discovery message
        to remove the component from homeassistant.
        :return:
        """
        name = "{!s}{!s}".format(COMPONENT_NAME, self._count)
        component_topic = _mqtt.getDeviceTopic(name)

        friendly_name = self._frn

        discover_switch = DISCOVERY_SWITCH + '"schema":"json",'
        if self._has_brightness:
            discover_switch += '"brightness":true, "brightness_scale":{}, '.format(self._light.scale())
        if self._has_rgb:
            discover_switch += '"rgb":true,'

        if register:
            await self._publishDiscovery(_COMPONENT_TYPE, component_topic, name, discover_switch,
                                         friendly_name)
        else:
            await self._deleteDiscovery(_COMPONENT_TYPE, name)
        del name, component_topic, friendly_name
        gc.collect()

    def _set_light(self, value):
        try:
            self.states['brightness'] = value['brightness']
            self._light.brightness(self.states['brightness'])
        except KeyError:
            pass
        try:
            self.states['color'] = value['color']
            self._light.color(self.states['color'])
        except KeyError:
            pass
        self.states['state'] = value['state']
        if self.states['state'] == 'ON':
            self._light.on()
        else:
            self._light.off()

    async def _transistion_loop(self, t_ms, target):
        start_time = time.ticks_ms()
        t = 0
        start = self.states.copy()

        while t < t_ms:
            current = {'state': 'ON'}
            try:
                current['brightness'] = start['brightness'] + \
                                              t * (target['brightness'] - start['brightness']) / t_ms
            except KeyError:
                pass
            try:
                for col in ['r', 'g', 'b']:
                    current['color'][col] = start['color'][col] + \
                                                  t * (target['color'][col] - start['color'][col]) / t_ms
            except KeyError:
                pass
            self._set_light(current)
            await _mqtt.publish(self._command_topic[:-4], json.dumps(self.states), qos=1)
            await asyncio.sleep(1)
            t = time.ticks_ms() - start_time

        self._set_light(target)
        await _mqtt.publish(self._command_topic[:-4], json.dumps(self.states), qos=1)

    async def on_set(self, topic, message, retained):
        """
        MQTTHandler is calling this subscribed async method whenever a message is received for the subscribed topic.
        :param topic: str
        :param message: str/dict/list (json converted)
        :param retained: bool
        :return:
        """
        try:
            transistion = message['transition']
            if self._loop_task is not None:
                self._loop_task.cancel()
            self._loop_task = asyncio.create_task(self._transistion_loop(transistion * 1000, message))
            return False
        except KeyError:
            self._set_light(message)
            return True
