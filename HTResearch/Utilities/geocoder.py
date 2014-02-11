import urllib2
from urllib import urlencode
from json import loads

google_geocode_url = "http://maps.googleapis.com/maps/api/geocode/json?"


def geocode(address, bounds=None, region=None,
            language=None, sensor=False, exactly_one=True, timeout=None):
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