# Geocode with Python
## What is Geocoding?
 Geocoding is the computational process of transforming a physical address description to a geographic locations (Latitude and Longitude).

## Installation
To geolocate a single address, I use Geopy python library. 

install libraries with Conda
```
conda install -c conda-forge geopy
conda install geopandas
```

## Geocoding
Under Geopy, using Nominatim Geocoding service, which is built on top of OpenStreetMap data.

```
import geopy
import geopandas
from geopy.geocoders import nominatim

geolocator = nominatim.Nominatim(user_agent="store_address")
location = geolocator.geocode ('606 W Katella Ave')

print(location.address)
print(location.latitude, location.longitude)
```

## Geocode many addresses from Pandas Dataframe
read the dataset
