import json
import random
import aiohttp
import asyncio



FORTNITE_PUBLIC_ENDPOINT = "https://fngw-mcp-gc-livefn.ol.epicgames.com/fortnite/api/game/v2/"
ACCOUNT_PUBLIC_ENDPOINT = "https://account-public-service-prod.ol.epicgames.com/account/api/"

NEW_SWITCH_AUTH = "basic OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3"
USER_AGENT = ""
SWITCH_HEADER = {
	"Authorization": NEW_SWITCH_AUTH,
	"User-Agent": USER_AGENT
}


class API:
	def __init__(self, acc):
		self.BASIC_IOS_HEADER = {
			'Authorization': NEW_SWITCH_AUTH,
			'User-Agent': USER_AGENT
		}

		self.acc = acc

	async def __aenter__(self):
		await self.Login()
		return self

	async def __aexit__(self, *exc):
		await self.Logout()

	def __enter__(self):
		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.Login())
		return self

	def __exit__(self, *exc):
		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.Logout())

	async def Login(self):
		if self.acc["secret"]:
			self.token = await self.GetFnTokenAuth()
	
		self.headers = {
			"Authorization": "bearer " + self.token,
			"User-Agent": USER_AGENT
		}

	async def Logout(self):
		url = "{}oauth/sessions/kill/{}".format(
			ACCOUNT_PUBLIC_ENDPOINT, self.token)
		async with aiohttp.ClientSession(headers=self.headers) as s:
			await s.delete(url, timeout=10)

	async def GetToken(self, login_data):
		url = "{}oauth/token".format(ACCOUNT_PUBLIC_ENDPOINT)
		async with aiohttp.ClientSession(headers=self.BASIC_IOS_HEADER) as s:
			async with s.post(url, data=login_data) as response:
				resp = await response.json()
		if "access_token" in resp:
			self.account_id = resp["account_id"]
			return resp["access_token"]
		else:
			if "errorMessage" in resp:
				resp["errorMessage"] = resp["errorMessage"].replace("'", "")
			raise Exception(resp)

	async def GetFnTokenAuth(self):
		login_data = {
			"grant_type": "device_auth",
			"secret": self.acc["secret"],
			"account_id": self.acc["account_id"],
			"device_id": self.acc["device_id"],
			"token_type": "eg1"
		}
		return await self.GetToken(login_data)

	async def QueryMCP(self, command, profile, body={}, rvn=-1):
		url = "{}profile/{}/client/{}?profileId={}&rvn={}".format(
			FORTNITE_PUBLIC_ENDPOINT, self.acc["account_id"], command, profile, rvn)
		if type(body) == str:
			body = json.loads(body)
		async with aiohttp.ClientSession(headers=self.headers) as s:
			async with s.post(url, json=body, timeout=20) as response:
				info = await response.json()
		if "errorMessage" in info:
			info["errorMessage"] = info["errorMessage"].replace("'", "")
			raise Exception(info)
		return info


	async def SetSaC(self, sacs):
		data = {
			"affiliateName": random.choice(sacs)
		}
		await self.QueryMCP("SetAffiliateName", "common_core", data)
		return True