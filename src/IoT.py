from hmac import HMAC
from base64 import b64encode, b64decode
from time import time
from urllib import parse
from hashlib import sha256

class IoT:
    class Device:
        def __init__(self, deviceId, hubName=[], dpsName=[]):
            self.deviceId = deviceId
            self.hubName = hubName
            self.dpsName = dpsName
        def __str__(self):
            return f'DeviceId: {self.deviceId}, HUBs: {self.hubName}, DPSs: {self.dpsName}'
        def __eq__(self, __value: object) -> bool:
            if self.deviceId == __value:
                return True
            return False

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

    def getDevicesWithoutDPS(self):
        count = 0
        for dev in self.devices.values():
            if dev.dpsName is [] and dev.hubName is not []:
                count += 1
        return count