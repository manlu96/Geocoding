# Geocode with Nominatim
## What is Geocoding?
 Geocoding is the computational process of transforming a physical address description to a geographic locations (Latitude and Longitude).

## Installation
To geolocate a single address, I use Geopy python library. 

install libraries with Conda
```
conda install -c conda-forge geopy
conda install geopandas
```

## Geocoding a single address
Under Geopy, using Nominatim Geocoding service, which is built on top of OpenStreetMap data.

```
import geopy
import geopandas
from geopy.geocoders import nominatim

geolocator = nominatim.Nominatim(user_agent="store_address")
location = geolocator.geocode ('606 W Katella Ave')

print(location.address)
print("Latitute = {}, Longitude = {}".format(location.latitude,location.longitude))
```

## Geocode many addresses from Pandas Dataframe
read the dataset: 

There are 5 rows x 28 columns in the dataframe 
The columns I need to use include Address1 (street address), City and State.

```
df = pd.read_csv("Locations.csv")
df.head()
```


delay geocoding 1 second between each address as service provider may deny access to the service if we are geocoding a large number of physical addresses

```
from geopy.extra.rate_limiter import RateLimiter
geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
```

## Preprocess the dataframe
```
full_addresses = []

for i in range(len(df)):
    address = []
    suite_location = df['Address1'].iloc[i].find('Suite')
    if suite_location == -1:
        address.append(df['Address1'].iloc[i])
    else:
        address1 = df['Address1'].iloc[i][0:suite_location].strip()
        address.append(address1)
    address.append(df['City'].iloc[i])
    address.append(df['State'].iloc[i])
    address = [str(s) for s in address]
    address = ','.join(address)
    full_addresses.append(address)  
df['Full Address'] = full_addresses
```
catch the timeout errors using geopy
```
from geopy.exc import GeocoderTimedOut

store_loc = df['Full Address'].apply(geocode, timeout=300)

store_loc
```
append latitude and longitude to the dataframe. 

After several tests, I found this nominatim method can geocode around 500 addresses at one time. 

```
latitude = []
for i in range(len(store_loc)):
    if store_loc.iloc[i] is not None:
        latitude.append(store_loc.iloc[i].latitude) 
    else:
        latitude.append(None)
df["Store_latitude"] = latitude


longitude = []
for i in range(len(store_loc)):
    if store_loc.iloc[i] is not None:
        longitude.append(store_loc.iloc[i].longitude) 
    else:
        longitude.append(None)

df["Store_longitude"] = longitude   

df.head(15)
```

# Geocode with GoogleMap
Python script for batch geocoding of addresses using the Google Geocoding API

```
import requests
import logging
import time

logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)

#create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
```

Set Google API key. the daily limit will be 2500.
With a "Google Maps Geocoding API" key from https://console.developers.google.com/apis/

*Example: API_KEY = 'AIzaSyC9azed9tLdjpZNjg2_kVePWvMIBq154eA'*

```
*API_KEY = 'please apply for your api key'*
BACKOFF_TIME = 30
output_filename = 'Locations_output.csv'
input_filename = 'Locations.csv'
address_column_name = "Address1"
RETURN_FULL_RESULTS = False
```

read the dataset: 
```
df1 = pd.read_csv("Locations.csv")

if address_column_name not in df1.columns:
    raise ValueError("Missing Address column in input data")
```

## Set up Geocoding url
```
def get_google_results(address, api_key=None, return_full_response=False):
    params = {
        'address': address,
        'key': api_key
    }
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    print(geocode_url)
    results = requests.get(geocode_url, params=params)
    results = results.json()
```

if there is no results or an error, return empty results
```
    if len(results['results']) == 0:
        output = {
            "formatted_address":None,
            "latitude":None,
            "longitude":None,
            "accuracy":None,
            "google_place_id":None,
            "type":None,
            "postcode":None
        }
    else:    
        answer = results['results'][0]
        output = {
            "formatted_address" : answer.get('formatted_address'),
            "latitude": answer.get('geometry').get('location').get('lat'),
            "longitude": answer.get('geometry').get('location').get('lng'),
            "accuracy": answer.get('geometry').get('location_type'),
            "google_place_id": answer.get("place_id"),
            "type": ",".join(answer.get('types')),
            "postcode": ",".join([x['long_name'] for x in answer.get('address_components') 
                                  if 'postal_code' in x.get('types')])
        }
    
    ##append some other details
    output['input_string'] = address
    output['number_of_results'] = len(results['results'])
    output['status'] = results.get('status')
    if return_full_response is True:
        output['response'] = results
    
    return output
```

test the result
```
test_result = get_google_results("27250 Madison Avenue,Temecula,CA", API_KEY, RETURN_FULL_RESULTS)

if test_result['status'] != 'OK':
    logger.warning("There was an error when testing the Google Geocoder.")
    raise ConnectionError('Problem with test results from Google Geocode - check your API key and internet connection.')
test_result
```