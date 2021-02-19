# pysmarttank

This repository implements the devices and components needed to create a fishtank controller with pysmartnode

## Setting up

The current implementation have been tested on ESP32.

First, clone Micropython SmartHome Node as detailed in https://github.com/kevinkk525/pysmartnode and deploy 
pysmartnode/pysmartnode and pysmartnode/micropython_mqtt_as onto the target.


It can be done by simply copying the libs into the VFS. I chose to freeze the two libraries into the firmware, so I can
test and change my code being sure I don't mess with pysmartnode.

Following the instruction from https://github.com/micropython/micropython/tree/master/ports/esp32, copy the two
libraries into micropython/port/esp32/modules, build and deploy the firmeware.

I had to reserve more space for the app partition than the default values, reducing the VFS partition to 1Mb
but that's good enough for me needs: edit micropython/port/esp32/partitions.csv

```
# Notes: the offset of the partition table itself is set in
# $ESPIDF/components/partition_table/Kconfig.projbuild and the
# offset of the factory/ota_0 partition is set in makeimg.py
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x6000,
phy_init, data, phy,     0xf000,  0x1000,
factory,  app,  factory, 0x10000, 0x280000,
vfs,      data, fat,     0x300000, 0x100000,
```



## Deployment

Adapt config.py and components.py to your needs and deploy the content of src/ onto the target.




