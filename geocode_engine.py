import logging
import time

import geopandas
import geopy
import pandas as pd
import requests
from geopy.geocoders import nominatim
from geopy.extra.rate_limiter import RateLimiter



class GeocodeEngine():

    def __init__(self):
        pass
    
    def _get_nominatim_results(self, addresses):

        ret = {'latitude': [], 'longitude': []}
        #return the latitude and longitute for the address
        locator = nominatim.Nominatim(user_agent="store_address")
        geocode = RateLimiter(locator.geocode, min_delay_seconds=1)

        for address in addresses:
            location = geocode(address)

            lat = None
            lng = None

            if location is not None:
                lat = location.latitude
                lng = location.longitude
            ret['latitude'].append(lat)
            ret['longitude'].append(lng)

        return ret
        
    def _get_google_results(addresses, api_key=None, return_full_response=False):
        
        ret = {'latitude': [], 'longitude': []}
        params = {
                'key': api_key
                }
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?"

        for address in addresses:
            params['address'] = address
            results = requests.get(geocode_url, params=params)
            results = results.json()

            lat = None
            lng = None
            if len(results['results']) != 0:
                answer = results['results'][0]
                lat = answer.get('geometry').get('location').get('lat')
                lng = answer.get('geometry').get('location').get('lng')
            ret['latitude'].append(lat)
            ret['longitude'].append(lng)
                
        return ret
    
    def _preprocess_address(self, df):
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
        return full_addresses  
        
        '''
        address = []
        suite_location = address_dict['Address1'].find('Suite')
        if suite_location == -1:
            address.append(address_dict['Address1'])
        else:
            address1 = address_dict['Address1'][:suite_location].strip()
            address.append(address1)
        address.append(address_dict['City'])
        address.append(address_dict['State'])
        address = [str(s) for s in address]
        address = ','.join(address)
        return address
        '''


    def get_geocode(self, address, geocoder_type="Nominatim", api_key=None, return_full_response=False):
        
        full_address = self._preprocess_address(address)
        if geocoder_type == "GoogleMap":
            geo_code = self._get_google_results(full_address, api_key=api_key, return_full_response=return_full_response)
        elif geocoder_type == "Nominatim":
            geo_code = self._get_nominatim_results(full_address)
        else:
            raise ValueError("geocoder not defined! Use either GoogleMap or Nominatim")
        ret = address.copy()
        ret = pd.concat([ret, pd.DataFrame(geo_code)], axis=1)
        return ret


if __name__ == '__main__':
    df = pd.read_csv("Locations.csv")
    geocode_engine = GeocodeEngine()
    # df=pd.DataFrame({"Address1":["11251 Beech Avenue","606 W.Katella Avenue"],"City":["Fontana","Orange"], "State":["CA","CA"]})
    print(geocode_engine.get_geocode(df.head()))

    