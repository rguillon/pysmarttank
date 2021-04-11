# Author: Renaud Guillon
# Copyright Renaud Guillon 2021 Released under the MIT license
# Created on 2021-04-09

"""
Subscribe to Home Assistant status topic and sends back the availability and status when Home Assistant becomes online
This can be usefull when Home Assistant restarts and loses the status of the devices

example config:
{
    package: .devices.ha_status_updater
    component: HaStatusUpdater
    constructor_args: {
        # mqtt_topic: custom mqtt topic  #optional, the mqtt topic to subscribe
    }
}
"""

__updated__ = "2021-04-09"
__version__ = "0.3"

import gc
from pysmartnode import config
from pysmartnode.utils.component import ComponentBase

COMPONENT_NAME = "HaStatusUpdater"

DEFAULT_TOPIC = 'homeassistant/status'

_mqtt = config.getMQTT()

gc.collect()

class HaStatusUpdater(ComponentBase):
    def __init__(self, mqtt_topic=None):

        super().__init__(COMPONENT_NAME, __version__, False)
        _mqtt.subscribeSync(
            mqtt_topic if mqtt_topic is not None else DEFAULT_TOPIC, self._process)

    async def _process(self, topic, msg, retain):
        if msg is "online":
            await _mqtt.publish(_mqtt.getDeviceTopic(config.MQTT_AVAILABILITY_SUBTOPIC), "online",
                                qos=1, retain=True)
            await config.getComponent("STATS")._publish()
