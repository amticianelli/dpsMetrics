import httpx
from src.IoT import IoT

class HUB(IoT):
    allDevices: list[str] = list()
    uniqueDevices: set[str] = set()
    duplicateDevices: set[dict] = set()
    
    def __init__(self, name, key, policyName):
        IoT.__init__(self, name, key, policyName)
        self.devices = list()
        self.URIs['default'] = f'{self.name}.azure-devices.net'
        self.URIs['iotHub'] = f'https://{self.name}.azure-devices.net/devices/query?api-version=2020-09-30'

    async def getDevices(self, isConTest):            

        async def responseAnalysis(response):
            for dev in response:
                dev['iothub'] = self.name
                iot = IoT()
                iot.addDevice(deviceId = dev['deviceId'], hubName=dev['iothub'])

            self.allDevices += response
            self.devices += response
            
            for dev in response:
                if dev['deviceId'] in self.duplicateDevices:
                    continue
                temp_len = len(self.uniqueDevices)
                self.uniqueDevices.add(dev['deviceId'])
                if temp_len == len(self.uniqueDevices):
                    self.uniqueDevices.remove(dev['deviceId'])
                    self.duplicateDevices.add(dev['deviceId'])

        self.generate_sas_token()

        headers: dict = {
            'Content-type': 'application/json',
            'Content-Encoding': 'utf-8',
            'Authorization': f'{self.sasToken}',
            'x-ms-max-item-count': '1000'
        }

        while True:
             
            async with httpx.AsyncClient() as client:
                result = await client.post(
                    url=self.URIs['iotHub'],
                    json={'query': 'SELECT deviceId FROM devices'},
                    headers=headers,
                    timeout=None
                )

            if result.status_code == 401:
                print(f'Token Invalid for {self.name}, generating another token')
                self.generate_sas_token()
                headers['Authorization'] = self.sasToken
                continue

            result.raise_for_status()
            if isConTest:
                print(f'Conn to {self.name} OK')
                break
            await responseAnalysis(result.json())

            continuation_token = result.headers.get("x-ms-continuation")
            if not continuation_token:
                break
            # Add the continuation token to the headers for the next request
            headers["x-ms-continuation"] = continuation_token
            continue

        print(f'Devices for {self.name} : {len(self.devices)}') if isConTest == False else None