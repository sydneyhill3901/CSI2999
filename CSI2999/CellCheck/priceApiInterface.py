import requests
import time

# Some Global Constants
JOBS_URL = "https://api.priceapi.com/v2/jobs"
KEY = "IZGKAZTOPLFCUFOEHEGGPBPBXUUSOIBAEAWSGNCHDLQNYRFGWWKHZOELEOZUYJCO" # LOL, remove this in prod, use env variables

def phoneQuery(searchTerm, key, apiURL=JOBS_URL, timeout=25, tries=0):
	""" Attempts to query the priceAPI for the product named productName searching
		both amazon and google-shopping. Two jobs will be created. The response for 
		the Amazon job wil be actively awaited until timeout is reached. At this time
		both jobs will be fetched if available. Default timeout is 25 seconds. In the case 1 job 
		fails, the other will still be returned
		Parameters:
			searchTerm: String to search using the API
			key: API key
			apiURL: URL to the priceAPI jobs service
			timeout: Timeout on the requests 
		Returns:
			- json in form of python dicitonary if 1 or more jobs complete
			- None on failure 
	"""
	validID = lambda i : i != None and i != "failed connection"
	ready = lambda Dict : Dict != None and ("status" in Dict and Dict["status"] == "ready")
	queries = {"amazon":None,"google":None}

	# Create the jobs, check success
	amzId = createSerchJob(searchTerm, "amazon", key, apiURL)
	googId = createSerchJob(searchTerm, "google_shopping", key, apiURL)
	if validID(amzId):
		queries["amazon"] = {"status":awaitResponse(amzId, key, timeout, apiURL)}	
		if validID(googId):
			queries["google"] = {"status":awaitResponse(googId, key, 5, apiURL)}
	elif validID(googId):
		# Only the google job was cread
		queries["google"] = {"status":awaitResponse(googId, key, 5, apiURL)}
	else:
		# Sucks, but we got nothing 
		return queries

	# get the results, or set the whole amazon association to None
	if ready(queries["amazon"]):
		queries["amazon"]["results"] = fetchResponse(amzId, key, apiURL)
		if queries["amazon"]["results"]:
			queries["amazon"]["success"] = queries["amazon"]["results"][0]["success"]
			queries["amazon"]["results"] = queries["amazon"]["results"][0]["content"]["search_results"]
		else:
			queries["amazon"]["results"] = None
			queries["amazon"]["success"] = False
	# Ditto for google
	if ready(queries["google"]):
		queries["google"]["results"] = fetchResponse(googId, key, apiURL)
		if queries["google"]["results"]:
			queries["google"]["success"] = queries["google"]["results"][0]["success"]
			queries["google"]["results"] = queries["google"]["results"][0]["content"]["search_results"]
		else:
			queries["google"]["results"] = None
			queries["gogle"]["success"] = False

	return queries

def createSerchJob(prodName, sourceSite, key, apiURL = JOBS_URL): 
		""" Returns:
			- id(jobIDstring) : on sucess
			- 'unauthorize' : when bad key given
			- 'service unavailable' : priceAPI server down
			- 'Bad Request' : Malformed query
			- 'Timeout' : on request timeout
			- '
		"""
		responseCodes = { 401 : "Unauthorized",
						  404 : "Not Found",
						  400 : "Bad Request",
						  408 : "Timeout",
						  418 : "They replaced the server with a teapot",
						  425 : "Too many requests",
						  500 : "Internal Server Error"
						 } 

		parameters = {   "token" : key, 
						  "source" : sourceSite, 
						  "country" : "us", 
						  "topic" : "search_results", 
						  "key" : "term", 
						  "values" : prodName, 
						  "timeout" : "1" 
					  } 
		try:
			job = requests.post(apiURL, parameters) 
			#Yay, job request worked! 
			code = job.status_code
			if code == 200: 
				try: 
					print("Job created") 
					return job.json()["job_id"] 
				except KeyError as e: 
					 print(f"Ooops, \n{e}") 
			else:
				if "reason" in job.json():
					print(f"Reason: {job.json()['reason']}")
					return None
				elif code in responseCodes:
					print(f"job failed to create, \n{responseCodes[code]}")		
					return None
				else:
					print("idk what happened")
					return None
		except ConnectionError as e:
			print(f"Connection failed in request")
			return "failed connection"


def awaitResponse(jobID, key, timeout, apiURL = JOBS_URL):
	""" Returns: 
			- none on failed request
			- 'request failure' if request failed
			- 'ready' if job completed sucessfully
			- 'not found' if job not found
			- 'invalid request' if request was invalid
			- 'request overload' if too many requests
			- 'cancelled': job cancelled
			- none: unknown issue
	"""
	failCodes = {404 : "not found",429 : "request overload",400 : "bad request",401 : "unauthorized"}	
	seconds = 0
	# Now we wait
	while seconds <= timeout:
		try:
			response = requests.get(f"{apiURL}/{jobID}?token={key}")
			code = response.status_code
			jsonResponse = response.json()
			if code != 200:
				print(f"Failed job, {failCodes[code]}")
				return failCodes[code]
			elif jsonResponse["status"] == "finished":
				print("Job ready")
				return "ready"
			elif jsonResponse["status"] == "cancelled":
				return "cancelled"
			elif jsonResponse["status"] in "new working finishing":
				if "progress" in jsonResponse:
					print("Status:",jsonResponse["status"],f"Progress:{jsonResponse['progress']}%")
				else:
					print("Status:",jsonResponse["status"])
			else:
				print("Something went very wrong..., got a response 200 w/o working, finished, or cancelled")
				print(f"status: {response.json()['status']}")
				return None
			# otherwise still waiting (response 200, status working
		except ConnectionError as e:
			print(f"looks like a request error \n{e}")
			return "request failure"
		except KeyError as e:
			print(f"Response code {code} is not in failCodes")
			return None
		print(f"waited for {seconds} seconds")
		seconds += 5
		time.sleep(5) # be polite

	return "Timeout"

def fetchResponse(jobID, key, apiURL= JOBS_URL):
	""" Returns:
			- on success : json in form of python dictionary
			- on fail : none 
	"""
	failCodes = {503 : "job not finished", 404 : "not found",429 : "request overload",400 : "bad request",401 : "unauthorized"}	
	try:
		response = requests.get(f"{apiURL}/{jobID}/download?token={key}")
		code = response.status_code
		if code == 200:
			print("Job sucessfully fetched!")
			return response.json()["results"]
		elif code == 302:
			# for performance reasons sometimes priceAPI serves data via a redirect
			print("Recieved redirect")
			try: 
				response = requests.get(response.json()["Location"])
				return response.json()["results"]
			except ConnectionError as e:
				print("redirected request failed\n {e}")
				return None
			except KeyError as e:
				print("Couldn't find 'Location' key , or 'results' key in response json dicitoanry")
				return None
		else:
			# something went awry
			print(f"Something went wrong: {failCodes[code]}")
			return None

	except ConnectionError as e:
		print(f"request failed!\n{e}")			
		return None
	except KeyError as e:
		print(f"key error occured\n{e}")
		return None



def filterResultList(phoneName,resultsList): 
	""" Takes in a phone name, and a list of PriceAPI search result dicitonaries. Returns a filtered list with  
		 blacklisted sites removed (ebay, phone carries) 
			- only correct phones 
			- unlocked phones  
			- Price in USD 
			- has a set price 
		- returns None if the final list is empty
	""" 
	blacklistNames = """ ebay ebay - marketplace sprint at&t verizon straight talk  """  
	phoneName = phoneName.lower()
	# Pay no mind to this hideous list of lambdas  
	filters = [ 
		lambda d : "name" in d and phoneName in d["name"].lower(), 
		lambda d : "name" in d and "unlocked" in d["name"].lower(), 
		lambda d : "price" in d or ("min_price" in d and ("max_price" in d and (d["min_price"] == d["max_price"]))), 
		lambda d : "currency" in d and d["currency"] == "USD", 
		lambda d : ("price" in d and int(d["price"].replace(".","")) != 0) or ("min_price" in d and int(d["min_price"].replace(".","")) != 0), 
		lambda d : not "shop_name" in d or not d["shop_name"].lower() in blacklistNames 
	] 
	# Filter out products which don't even have the phone name  
	# apply remaining filters 
	filtered = resultsList 
	for f in filters: 
		filtered = filter(f,filtered)
	
	# Filter out "plus" models when looking for non-plus models
	if not "+" in phoneName or not "plus" in phoneName:
		filtered = filter(lambda d : not "+" in d["name"] and not "plus" in d["name"] , filtered)


	# If the filtered list isn't empty, then return it. Return none otherwise
	filtered = list(filtered)
	if filtered:
		return filtered
	return None
