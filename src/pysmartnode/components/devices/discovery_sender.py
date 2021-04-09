# Author: Renaud Guillon
# Copyright Renaud Guillon 2021 Released under the MIT license
# Created on 2021-04-09

"""
Subscribe to a topic and resend the doscovery from every created components when a message is received.
This can be usefull when Home Assistant has been restared and lsot the discovered devices.
example config:
{
    package: .devices.discovery_sender
    component: DiscoverySender
    constructor_args: {
        # mqtt_topic: custom mqtt topic  #optional, the mqtt topic to subscribe to listen to send discovery request
    }
}
"""

__updated__ = "2021-03-21"
__version__ = "0.1"

import gc
from pysmartnode import config
from pysmartnode.utils.component import ComponentBase, _components

COMPONENT_NAME="DiscoverySender"
DEFAULT_TOPIC='ResendDiscovery'

_mqtt = config.getMQTT()

gc.collect()


class DiscoverySender(ComponentBase):
    def __init__(self, mqtt_topic=None):
        
        super().__init__(COMPONENT_NAME, __version__, False)
        
        _mqtt.subscribeSync(
            mqtt_topic if mqtt_topic is not None else "{}/{}".format(config.MQTT_HOME, DEFAULT_TOPIC),
            self._process)

    async def _process(self, topic, msg, retain):
        c = _components
        while c is not None:
            await c._discovery()
            gc.collect()
            c = c._next_component
