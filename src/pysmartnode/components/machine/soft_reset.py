# Author: Renaud Guillon
# Copyright Renaud Guillon 2021 Released under the MIT license
# Created on 2021-03-21

"""
example config:
{
    package: .switches.soft_reset
    component: SOFT_RESET
    constructor_args: {
        # instance_name: name  #optional, name of the instance, will be generated automatically
    }
}
"""

__updated__ = "2021-03-21"
__version__ = "0.1"

import gc
import machine

from pysmartnode import config
from pysmartnode.utils.component.switch import ComponentSwitch

_mqtt = config.getMQTT()

COMPONENT_NAME = "SOFT_RESET"
_COMPONENT_TYPE = "soft_reset"
_unit_index = -1

gc.collect()


class SoftReset(ComponentSwitch):
    def __init__(self, mqtt_topic=None, instance_name=None, **kwargs):
        mqtt_topic = mqtt_topic or _mqtt.getDeviceTopic(
            "{!s}".format(COMPONENT_NAME), is_request=True)
        global _unit_index
        _unit_index += 1
        super().__init__(COMPONENT_NAME, __version__, _unit_index, mqtt_topic=mqtt_topic,
                         instance_name=instance_name or "{!s}".format(COMPONENT_NAME),
                         **kwargs)

    async def _on(self):
        machine.soft_reset()
        return True