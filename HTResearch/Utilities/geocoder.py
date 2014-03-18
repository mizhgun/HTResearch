#
# geocoder.py
# A module with functions for geocoding addresses for Google Maps.
#

import urllib2
from urllib import urlencode
from json import loads

#region Globals
google_geocode_url = "http://maps.googleapis.com/maps/api/geocode/json?"
#endregion


def geocode(address, bounds=None, region=None,
            language=None, sensor=False, exactly_one=True):
    """
    Geocodes an address.

    address - The address to geocode.
    bounds - The bounds for geocoding.
    region - The region for geocoding.
    language - The specific language for geocoding.
    sensor - Whether or not a GPS sensor is present (false by default).
    exactly_one - Whether or not to encode exactly one item (true by default).
    """

    params = {
        'address': address.encode('ascii', 'ignore'),
        'sensor': str(sensor).lower()
    }
    if bounds:
        params['bounds'] = bounds
    if region:
        params['region'] = region
    if language:
        params['language'] = language

    url = google_geocode_url + urlencode(params)
    response = urllib2.urlopen(url)
    bob = response.read()
    jsongeocode = loads(bob)
    return _parse_json(jsongeocode, exactly_one)


def _parse_json(page, exactly_one=True):
    # Returns location, (latitude, longitude) from json feed.

    places = page.get('results', [])
    if not len(places):
        return None

    def parse_place(place):
        # Get the location, lat, lng from a single json place.
        latitude = place['geometry']['location']['lat']
        longitude = place['geometry']['location']['lng']
        return [latitude, longitude]

    if exactly_one:
        return parse_place(places[0])
    else:
        return [parse_place(place) for place in places]