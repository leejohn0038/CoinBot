import sys
import time
import math
import base64
import hmac, hashlib
import urllib.parse
import pycurl
import json
import asyncio
import time

start = time.time()
ver = []
global flag
flag = 1
class XCoinAPI:
	api_url = "https://api.bithumb.com"
	

	def __init__(self, api_key, api_secret):
		self.api_key = api_key
		self.api_secret = api_secret

	def body_callback(self, buf):
		self.contents = buf

	def microtime(self, get_as_float = False):
		if get_as_float:
			return time.time()
		else:
			return '%f %d' % math.modf(time.time())

	def usecTime(self) :
		mt = self.microtime(False)
		mt_array = mt.split(" ")[:2]
		return mt_array[1] + mt_array[0][2:5]

	async def xcoinApiCall(self, endpoint, rgParams, i):
	
		endpoint_item_array = {
			"endpoint" : endpoint
		}

		uri_array = dict(endpoint_item_array, **rgParams)

		str_data = urllib.parse.urlencode(uri_array)

		nonce = self.usecTime()

		data = endpoint + chr(0) + str_data + chr(0) + nonce
		utf8_data = data.encode('utf-8')

		key = self.api_secret
		utf8_key = key.encode('utf-8')

		h = hmac.new(bytes(utf8_key), utf8_data, hashlib.sha512)
		hex_output = h.hexdigest()
		utf8_hex_output = hex_output.encode('utf-8')

		api_sign = base64.b64encode(utf8_hex_output)
		utf8_api_sign = api_sign.decode('utf-8')


		curl_handle = pycurl.Curl()
		curl_handle.setopt(pycurl.POST, 1)
		curl_handle.setopt(pycurl.POSTFIELDS, str_data)

		url = self.api_url + endpoint
		curl_handle.setopt(curl_handle.URL, url)
		curl_handle.setopt(curl_handle.HTTPHEADER, ['Api-Key: ' + self.api_key, 'Api-Sign: ' + utf8_api_sign, 'Api-Nonce: ' + nonce])
		curl_handle.setopt(curl_handle.WRITEFUNCTION, self.body_callback)
		await loop.run_in_executor(None, curl_handle.perform)

		curl_handle.close()

	async def order(self, ep1, rgParams, i):

		self.xcoinApiCall(ep1, rgParams, i)

async def main():
	api_key = "api-key"
	api_secret = "secret-key"	
	b = "/trade/market_buy"
	s = "/trade/market_sell"
	c = {
	'units' : 1,
	"order_currency" : "BTC",
	"payment_currency" : "KRW"
	}
	a = XCoinAPI(api_key, api_secret)

	futures = [asyncio.create_task(a.xcoinApiCall(b,c,i)) for i in range(500)]
	await asyncio.gather(*futures)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()

print(time.time() - start)