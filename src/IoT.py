from hmac import HMAC
from base64 import b64encode, b64decode
from time import time
from tkinter import N
from urllib import parse
from hashlib import sha256
import pandas as pd

class Device:
    def __init__(self, deviceId, hubList=set(), dpsList=set()):
        self.deviceId = deviceId
        self.hubList = hubList
        self.dpsList = dpsList
    
    def __repr__(self):
        return f'''
        DeviceId: {self.deviceId}
        Hub List: {self.hubList}
        DPS List: {self.dpsList}
'''

    def __str__(self):
        return f'''
        DeviceId: {self.deviceId}
        Hub List: {self.hubList}
        DPS List: {self.dpsList}
'''
    
    def toDict(self):
        return {
            'deviceId': self.deviceId,
            'hubList': self.hubList,
            'dpsList': self.dpsList
        }
    
class IoT:
    devices = {}
    def __init__(self, name='', key='', policyName=''):
        self.name = name
        self.key = key
        self.policyName = policyName
        self.URIs = dict()

    def generate_sas_token(self, expiry=3600):
        ttl = time() + expiry
        sign_key = "%s\n%d" % ((parse.quote_plus(self.URIs['default'])), int(ttl))
        #print(sign_key)
        signature = b64encode(HMAC(b64decode(self.key), sign_key.encode('utf-8'), sha256).digest())

        rawtoken = {
            'sr' :  self.URIs['default'],
            'sig': signature,
            'se' : str(int(ttl)),
            'skn' : self.policyName
        }
        self.sasToken = 'SharedAccessSignature ' + parse.urlencode(rawtoken)

    def addDevice(self, deviceId, hubName=None, dpsName=None):            
        if deviceId not in self.devices.keys():
            self.devices[deviceId] = Device(deviceId=deviceId)
        if hubName is not None:
            self.devices[deviceId].hubList.add(hubName)
        if dpsName is not None:
            self.devices[deviceId].dpsList.add(dpsName)

    def createDF(self):
        df = []
        for dev in self.devices.values():
            df.append(dev.toDict())
        return pd.DataFrame(df)

    def getDevicesWithoutDPS(self):
        count = 0
        for dev in self.devices.values():
            if len(dev.dpsName) == 0 and len(dev.hubName) > 0:
                count += 1
        return count