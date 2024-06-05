# dpsMetrics

## Architecture
![alt text](https://github.com/amticianelli/dpsMetrics/blob/main/img/image.png)

## Features
* Number of group registrations per DPS instance
* Number of devices per Hub
* Comparison between DPS registrations and Hub devices
* List of devices without DPS and DPS registrations without an assigned hub

## Limitations
* It may take some time to retrieve all the devices / registrations, seeing that we are using paginated REST APIs
* Shared access keys are at the momment the only possible way of authenticating

## How to use it
 
* Copy the file data_template renaming it to data.yaml
* If not running inside a dev container, install the dependecies:
    * pip install -r requirements.txt
* Run with
```shellscript
python main.py
```
* Example output:
```shellscript
Conn to iotalblab OK
Conn to iotlabalbgw1 OK
Conn to dpsalblab and group cax509test OK
Conn to dpsalblab and group groupexamplealb OK
Conn to dpsalblab and group testOrange OK
Conn to osama-iot-dps and group iotedge-centos OK
Conn to osama-iot-dps and group test OK
Devices for iotalblab : 1023
Devices for iotlabalbgw1 : 995
TOTAL NUMBER OF DEVICES: 2018
Registrations for dpstest2 : 0
Registrations for osama-iot-dps : 4
Registrations for dpsalblab : 2003
TOTAL NUMBER OF REGISTRATIONS: 2007
┌───────────────┬─────────────────┐
│    dpsname    │ devicesNotInHub │
│    varchar    │      int64      │
├───────────────┼─────────────────┤
│ osama-iot-dps │               4 │
└───────────────┴─────────────────┘

┌──────────────┬──────────────────────┐
│    iothub    │ devicesWithoutDPSReg │
│   varchar    │        int64         │
├──────────────┼──────────────────────┤
│ iotalblab    │                   12 │
│ iotlabalbgw1 │                    3 │
└──────────────┴──────────────────────┘
```

## Next steps
* AD / Entra authentication
* Individual enrollment count


## Creators
* Alberto M. Tizianel
* Osama Awadallah
