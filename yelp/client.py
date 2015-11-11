# -*- coding: UTF-8 -*-
import json
import urllib
import urllib2

from yelp.config import API_HOST
from yelp.config import BUSINESS_PATH
from yelp.config import PHONE_SEARCH_PATH
from yelp.config import SEARCH_PATH
from yelp.errors import ErrorHandler
from yelp.obj.business_response import BusinessResponse
from yelp.obj.search_response import SearchResponse


class Client(object):

    def __init__(self, authenticator):
        self.authenticator = authenticator
        self._error_handler = ErrorHandler()

    def get_business(self, business_id, **url_params):
        """Make a request to the business endpoint. More info at
        https://www.yelp.com/developers/documentation/v2/business

        Args:
            business_id (str): The business id.
            **url_params: Dict corresponding to business API params
                https://www.yelp.com/developers/documentation/v2/business#lParam

        Returns:
            BusinessResponse object that wraps the response.

        """
        business_path = BUSINESS_PATH + business_id
        return BusinessResponse(self._make_request(business_path, url_params))

    def search(
        self,
        location,
        current_lat=None,
        current_long=None,
        **url_params
    ):
        """Make a request to the search endpoint. Specify a location by
        neighbourhood, address, or city. More info at
        https://www.yelp.com/developers/documentation/v2/search_api#searchNAC

        Args:
            location (str): A string that specifies location by neighbourhood,
                address, or city.
            current_lat (float): Optional latitude to disambiguate location.
            current_long (float): Optional longitude to disambiguate location.
            **url_params: Dict corresponding to search API params
                https://www.yelp.com/developers/documentation/v2/search_api#searchGP

        Returns:
            SearchResponse object that wraps the response.

        """
        url_params.update({
            'location': location
        })
        if current_lat is not None and current_long is not None:
            url_params['cll'] = self._format_current_lat_long(
                current_lat,
                current_long
            )

        return SearchResponse(self._make_request(SEARCH_PATH, url_params))

    def search_by_bounding_box(
        self,
        sw_latitude,
        sw_longitude,
        ne_latitude,
        ne_longitude,
        **url_params
    ):
        """Make a request to the search endpoint by bounding box. Specify a
        southwest latitude/longitude and a northeast latitude/longitude. See
        http://www.yelp.com/developers/documentation/v2/search_api#searchGBB

        Args:
            sw_latitude (float): Southwest latitude of bounding box.
            sw_longitude (float): Southwest longitude of bounding box.
            ne_latitude (float): Northeast latitude of bounding box.
            ne_longitude (float): Northeast longitude of bounding box.
            **url_params: Dict corresponding to search API params
                https://www.yelp.ca/developers/documentation/v2/search_api#searchGP

        Returns:
            SearchResponse object that wraps the response.

        """
        url_params['bounds'] = self._format_bounds(
            sw_latitude,
            sw_longitude,
            ne_latitude,
            ne_longitude
        )

        return SearchResponse(self._make_request(SEARCH_PATH, url_params))

    def search_by_coordinates(
        self,
        latitude,
        longitude,
        accuracy=None,
        altitude=None,
        altitude_accuracy=None,
        **url_params
    ):
        """Make a request to the search endpoint by geographic coordinate.
        Specify a latitude and longitude with optional accuracy, altitude, and
        altitude_accuracy. More info at
        http://www.yelp.com/developers/documentation/v2/search_api#searchGC

        Args:
            latitude (float): Latitude of geo-point to search near.
            longitude (float): Longitude of geo-point to search near.
            accuracy (float): Optional accuracy of latitude, longitude.
            altitude (float): Optional altitude of geo-point to search near.
            altitude_accuracy (float): Optional accuracy of altitude.
            **url_params: Dict corresponding to search API params
                https://www.yelp.ca/developers/documentation/v2/search_api#searchGP

        Returns:
            SearchResponse object that wraps the response.

        """
        url_params['ll'] = self._format_coordinates(
            latitude,
            longitude,
            accuracy,
            altitude,
            altitude_accuracy
        )

        return SearchResponse(self._make_request(SEARCH_PATH, url_params))

    def phone_search(self, phone, **url_params):
        """Make a request to the phone search endpoint.More info at
        https://www.yelp.com/developers/documentation/v2/phone_search

        Args:
            phone (str): Business phone number to search for.
            **url_params: Dict corresponding to phone search API params
                https://www.yelp.com/developers/documentation/v2/phone_search

        Returns:
            SearchResponse object that wraps the response.

        """
        url_params['phone'] = phone

        return SearchResponse(
            self._make_request(PHONE_SEARCH_PATH, url_params)
        )

    def _format_current_lat_long(self, lat, long):
        return '{0},{1}'.format(lat, long)

    def _format_bounds(
        self,
        sw_latitude,
        sw_longitude,
        ne_latitude,
        ne_longitude
    ):
        return '{0},{1}|{2},{3}'.format(
            sw_latitude,
            sw_longitude,
            ne_latitude,
            ne_longitude
        )

    def _format_coordinates(
        self,
        latitude,
        longitude,
        accuracy,
        altitude,
        altitude_accuracy
    ):
        coord = '{0},{1}'.format(latitude, longitude)
        for field in (accuracy, altitude, altitude_accuracy):
            if field is not None:
                coord += ',' + str(field)
            else:
                break
        return coord

    def _make_request(self, path, url_params={}):
        url = 'https://{0}{1}?'.format(
            API_HOST,
            urllib.quote(path.encode('utf-8'))
        )
        signed_url = self.authenticator.sign_request(url, url_params)
        return self._make_connection(signed_url)

    def _make_connection(self, signed_url):
        try:
            conn = urllib2.urlopen(signed_url, None)
        except urllib2.HTTPError as error:
            self._error_handler.raise_error(error)
        else:
            try:
                response = json.loads(conn.read())
            finally:
                conn.close()
            return response
