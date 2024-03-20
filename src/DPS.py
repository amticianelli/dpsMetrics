from jinja2 import Template
import httpx
import time
import json
from src.IoT import IoT
import asyncio

class DPS(IoT):
    allRegistrations: list[str] = list()
    uniqueRegistrations: set[str] = set()
    duplicateRegistrations: set[dict] = set()

    def __init__(self, name, key, policyName):
        IoT.__init__(self, name, key, policyName)
        self.registrations = list()
        self.groups = list()
        self.URIs['default'] = f'{self.name}.azure-devices-provisioning.net'
        self.URIs['getGroups'] = f'https://{self.URIs['default']}/enrollmentGroups/query?api-version=2021-06-01'
        self.URIs['dpsRegistrations'] = Template('https://' + f'{self.name}' + '.services.azure-devices-provisioning.net/registrations/{{group}}/query?api-version=2021-06-01')
    
    async def getDPSGroups(self):
        self.generate_sas_token()
        headers: dict = {
            'Content-type': 'application/json',
            'Content-Encoding': 'utf-8',
            'Authorization': f'{self.sasToken}',
            'x-ms-max-item-count': '1000'
        }

        async with httpx.AsyncClient() as client:
            result = await client.post(
                url=self.URIs['getGroups'],
                headers=headers,
                json={'query': ''},
                timeout=None
            )
        self.groups = [group['enrollmentGroupId'] for group in result.json()]

    async def getDPSRegistrations(self, isConTest=False):
        await self.getDPSGroups()            

        async def responseAnalysis(response):
            for reg in response:
                del reg['createdDateTimeUtc']
                del reg['substatus']
                del reg['lastUpdatedDateTimeUtc']
                del reg['etag']
                reg['dpsname'] = self.name
                reg['assignedHub'] = reg['assignedHub'].split('.')[0]
            
            self.allRegistrations += response
            self.registrations += response

            for reg in response:
                if reg['deviceId'] in self.duplicateRegistrations:
                    continue
                temp_len = len(self.uniqueRegistrations)
                self.uniqueRegistrations.add(reg['deviceId'])
                if temp_len == len(self.uniqueRegistrations):
                    self.uniqueRegistrations.remove(reg['deviceId'])
                    self.duplicateRegistrations.add(reg['deviceId'])    
        
        self.generate_sas_token()

        headers: dict = {
            'Content-type': 'application/json',
            'Content-Encoding': 'utf-8',
            'Authorization': f'{self.sasToken}',
            'x-ms-max-item-count': '1000'
        }
        payload: dict = {
            "query": "SELECT registrationId,assignedHub,status FROM deviceregistration"
        }

        for group in self.groups:
            while True:
                try:
                    async with httpx.AsyncClient() as client:
                        result = await client.post(
                            url=self.URIs['dpsRegistrations'].render(group=group),
                            json=payload,
                            headers=headers,
                            timeout=None
                        )
                except BaseException as e:
                    if isinstance(e, httpx.ConnectTimeout):
                        print(f'Connection to {self.name} and group {group} timed out')
                        time.sleep(10)
                        continue
                    else:
                        print(f'Connection to {self.name} and group {group} failed')
                        time.sleep(10)
                        continue
                if result.status_code == 401:
                        print(f'Token Invalid for {self.name}, generating another token')
                        self.generate_sas_token()
                        headers['Authorization'] = self.sasToken
                        continue
                result.raise_for_status()

                if isConTest:
                    print(f'Conn to {self.name} and group {group} OK')
                    break

                await responseAnalysis(response=result.json())

                continuation_token = result.headers.get("x-ms-continuation")
                if not continuation_token:
                    break
                # Add the continuation token to the headers for the next request
                headers["x-ms-continuation"] = continuation_token
                
        print(f'Registrations for {self.name}: {len(self.registrations)}') if isConTest == False else None
