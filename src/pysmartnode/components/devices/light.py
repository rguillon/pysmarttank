# Author: Renaud Guillon
# Copyright Renaud Guillon 2021 Released under the MIT license
# Created on 2021-02-16

"""
Light component implementing a subset of homeassistant light devices. Basic on/off lights, lights with brightness and
RGB lights are supported, including the transitions.

example config for Light:
{
	package: .devices.lightd
    component: Light
    constructor_args: {
        # friendly_name: null    # optional, friendly name shown in homeassistant gui with mqtt discovery
        # discover: true         # optional, if false no discovery message for homeassistant will be sent.
	    has_brightness: True if the Ligh shall manage brightness
	    has_rgb:        True if the Ligh shall manage rgb
	    light: the object that will drive the physical output(s)
    }
}l
"""

__updated__ = "2021-04-09"
__version__ = "0.5"

import gc
import time

import uasyncio as asyncio
from pysmartnode import logging
from pysmartnode import config
from pysmartnode.utils.component import ComponentBase, DISCOVERY_SWITCH

COMPONENT_NAME = "Light"
_COMPONENT_TYPE = "light"

_log = logging.getLogger(COMPONENT_NAME)
_mqtt = config.getMQTT()
gc.collect()
import json

_unit_index = -1


class Light(ComponentBase):
    def __init__(self, friendly_name=None, discover=True, light1=None, lightG=None, lightB=None, has_brightness=True, has_rgb=True, **kwargs):
        """
        :param friendly_name: friendly name shown in homeassistant gui with mqtt discovery
        :param discover:
        :param light1: the object that will be called to drive the light, is expected to have a setDuty  and a scale
                       method, in case of RGB, this light will be used for red
        :param lightG: the object called to set the Green light
        :param lightB: the object called to set the Blue light
        :param has_brightness: true if the light shall manage brightness
        :param has_rgb: true if the light shall manage rgb
        """
        global _unit_index
        _unit_index += 1
        super().__init__(COMPONENT_NAME, __version__, _unit_index, discover=discover, **kwargs)

        self._command_topic = _mqtt.getDeviceTopic(
            "{!s}{!s}".format(COMPONENT_NAME, self._count), is_request=True)
        _mqtt.subscribeSync(self._command_topic, self.on_set, self, check_retained_state=True)

        self._frn = friendly_name
        self._light1 = light1
        self._lightG = lightG
        self._lightB = lightB

        self.states = {'state': 'OFF'}
        self._has_brightness = has_brightness
        if self._has_brightness:
            self.states['brightness'] = 0
        self._has_rgb = has_rgb
        if self._has_rgb:
            self.states['color'] = {'r':255, 'g':255, 'b':255}

        self._transition_task = None
        gc.collect()

    async def _init_network(self):
        await super()._init_network()


    async def _remove(self):
        """Will be called if the component gets removed"""
        # Cancel any loops/asyncio coroutines started by the component
        if self._transition_task is not None:
            self._transition_task.cancel()
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
        # For some reason homeassistant needs a json schema to accept brightness and rgb
        discover_switch = DISCOVERY_SWITCH + '"schema":"json",'
        if self._has_brightness:
            discover_switch += '"brightness":true, "brightness_scale":{}, '.format(self._light1.scale())
        if self._has_rgb:
            discover_switch += '"rgb":true,'

        if register:
            await self._publishDiscovery(_COMPONENT_TYPE, component_topic, name, discover_switch,
                                         friendly_name)
        else:
            await self._deleteDiscovery(_COMPONENT_TYPE, name)
        del name, component_topic, friendly_name
        # send the full state on startup so the HA has the same values as the device
        await self._send_full_state()
        gc.collect()

    async def _set_light(self, value):
        try:
            self.states['state'] = value['state']
        except KeyError:
            pass

        if not self._has_brightness:
            if self.states['state'] is 'ON':
                self._light1.setDuty(self._light.scale())
            else:
                self._light1.setDuty(0)
        else:
            try:
                self.states['brightness'] = value['brightness']
            except KeyError:
                pass

            # do not modify the saved brightness if the state is off as HA will expect the light to keep the same
            # brightness when putting it back on
            is_off = False
            try:
                if value['state'] is 'OFF':
                    is_off = True
            except KeyError:
                pass


            if self._has_rgb:
                try:
                    self.states['color'] = value['color']
                except KeyError:
                    pass
                # RGB values are always in the 0..255 range in HA, no matter the scale
                self._light1.setDuty(0 if is_off else self.states['brightness'] * self.states['color']['r'] / 255)
                self._lightG.setDuty(0 if is_off else self.states['brightness'] * self.states['color']['g'] / 255)
                self._lightB.setDuty(0 if is_off else self.states['brightness'] * self.states['color']['b'] / 255)
            else:
                self._light1.setDuty(0 if is_off else self.states['brightness'])
        await self._send_full_state()

    async def _send_full_state(self):
        await _mqtt.publish(self._command_topic[:-4], json.dumps(self.states), qos=1)

    async def _transition_loop(self, t_ms, target):
        """
        A transition loop that will reach the target state in the given amount of time.
        :param t_ms: the transition time in milliseconds
        :param target: the target state
        :return:²
        """
        start_time = time.ticks_ms()
        t = 0
        start = self.states.copy()
        print("start :")
        print(start)
        print("target :")
        print(target)

        # For light_off with a transition, HA sends no brightness
        try:
            if target['state'] is 'OFF':
                target['brightness'] = 0
        except KeyError:
            pass

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
            await self._set_light(current)
            await asyncio.sleep(1)
            t = time.ticks_ms() - start_time

        await self._set_light(target)


    async def on_set(self, topic, message, retained):
        """
        MQTTHandler is calling this subscribed async method whenever a message is received for the subscribed topic.
        :param topic: str
        :param message: str/dict/list (json converted)
        :param retained: bool
        :return:
        """
        # cancel any transition in progress
        if self._transition_task is not None:
            self._transition_task.cancel()
        try:
            transition = message['transition']
            self._transition_task = asyncio.create_task(self._transition_loop(transition * 1000, message))
        except KeyError:
            await self._set_light(message)
        # set light will already send the new state
        return False
