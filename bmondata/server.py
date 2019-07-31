"""Holds the Server class, which allows access to the data on one BMON server.
"""
from urllib.parse import urljoin
import re
import json
import requests
import pandas as pd

# Minimum required version of the BMON API.
MIN_API_VERSION =  2.0

def check_response(resp_dict):
    """Analyzes the dictionary response from an API call, 'resp_dict';
    if the response indicates an error, raise an appropriate Exception, 
    otherwise return 'resp_dict'.
    """
    if resp_dict['status'] == 'success':
        return resp_dict
    elif resp_dict['status'] == 'fail':
        raise ValueError(f"Bad Argument: {resp_dict['data']}")
    else:
        raise RuntimeError(f"Error at server: {resp_dict['message']}") 


class Server:

    def __init__(self, base_url, store_key=None):
        """ Parameters:
        base_url: The base URL of the BMON server, e.g. 'https://bmon.analysisnorth.com'.
            Should include protocol, domain, and subdomain (if present).
        store_key: If you intend to use the 'store_sensor_readings' method of this
            class, you must provide the secret store_key for the BMON server you are 
            accessing.  This key is present in the 'settings.py' file on the BMON server. 
        """

        # make a call to the server to see if it is accessible
        # make-store-key method has been around since the beginning.
        try:
            requests.get(urljoin(base_url, 'make-store-key/'))
        except:
            raise ValueError(f'{base_url} is not available or is not a BMON server.')

        # make sure the BMON server is running a recent enought API version
        try:
            resp = requests.get(urljoin(base_url, 'api/v2/version/')).json()
        except:
            # old versions did not have a version property.
            raise ValueError(f'{base_url} is not running a current enough version of BMON.')
        
        if resp['data']['version'] < MIN_API_VERSION:
            raise ValueError(f'{base_url} is not running a current enough version of BMON.')

        self.base_url = base_url
        self.store_key = store_key

    def _url(self, url_part):
        """Helper method for making BMON URLs.
        """
        return urljoin(self.base_url, url_part)

    def sensor_readings(
            self,
            sensors,
            start_ts = None,
            end_ts = None,
            timezone = None,
            averaging = None,
            label_offset = None
        ):
        """Retrieves sensor readings from one or more sensor ands presents them in a Pandas
        DataFrame.  Has the ability to filter by readings by time, and perform time averaging.
        
        Parameters:
            sensors: The list of sensors that readings should be retrieved for.  The format of
                this parameter is flexible. It can be a list of Sensor IDs(of type string) or it
                 can be one Sensor ID not in a list. Examples:
                    sensors = ['kwethluk_temp', 'kwethluk_wind']   # list of Sensor IDs
                    sensors = 'kwethluk_temp'     # one Sensor ID
                Any or all sensors can have a label that will be used as the Pandas column name
                instead of the Sensor ID.  If you want a label for a sensor, use a two-tuple that
                includes the Sensor ID and the label.  This example substitutes the label 'temperature'
                for the Sensor ID 'kwethluk_temp' but does not use a substitute label for 'kwethluk_wind'.
                    sensors = [
                        ('kwethluk_temp', 'temperature'),
                        'kwethluk_wind'
                    ]
            start_ts: The earliest date/time to include in the sensor readings. The format of this
                parameter is a string date/time that can be parsed by the dateutil.parser.parse
                function, which is very flexible.  If the parameter is None, the earliest readings
                available are included.
            end_ts: The latest date/time to include in the sensor readings.  String date/time format.
                A value of None will include readings through the latest available.
            timezone: The timezone that applies to start_ts, end_ts, and the the timestamps of the
                returned sensor readings.  This is a string value and must be one of the values
                in the list pytz.all_timezones.  If it is not provided, the most prevalent timezone
                found for the buildings associated with the sensor list is used.  If there are no
                timezones specified for the buildings, UTC is the assumed timezone.
            averaging: Setting this parameter to a DateOffset string, as described here:
                https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
                will cause the sensor readings to be averaged into time intervals.  For example, an
                'averaging' value of '2H' will cause readings to be averaged into 2 hour intervals.
                A value of None for this parameter causes no averaging to occur.
            label_offset: Only relevant if 'averaging' is specified.  This parameter determines what
                time point in the averaging interval is used to mark the data point.  The default is
                to use the time at the left edge (earliest) point in the interval (label_offset = None).
                A non-None value specifies an offset from the left edge of the interval; for example,
                a value of '15min' means to label the averaged sensor reading with the time that is
                15 minutes later than the beginning of the interval.
  
        Returns:
            Pandas DataFrame, indexed by date/time of readings, separate column for each sensor.
            A special attribute is assigned to the DataFrame that holds the timezone associated
            with the date/times of the readings.  That attribute is 'bmon_timezone'; if 'df' is a
            variable pointing to the DataFrame, df.bmon_timzone returns a string indicating the
            timezone of the readings in the DataFrame.
        """

        # Process the 'sensors' parameter.  If it is a single string, then
        # it is one sensor ID.  If it is a tuple, then it is probably one sensor
        # ID with a label.  If it is a list, then it is a list of sensor IDs, possibly
        # with labels for some of the sensors.
        # Objective here is to make a clean list of sensor IDs and a dictionary
        # mapping sensor IDs to substitute labels.
        if type(sensors) is str:
            sensor_id_list = [sensors]
            sensor_labels = {}
        elif type(sensors) is tuple:
            # guessing that this is a two tuple with one sensor ID 
            # along with a substitute label.
            if len(sensors) != 2:
                raise ValueError('Incorrectly formatted sensors.') 
            sensor_id_list =[sensors[0]]
            sensor_labels = {sensors[0]: sensors[1]}
        elif type(sensors) is list:
            # list of sensor IDs possible with substitute labels
            sensor_id_list = []
            sensor_labels = {}
            for sensor_info in sensors:
                if type(sensor_info) is str:
                    # just a sensor ID
                    sensor_id_list.append(sensor_info)
                elif type(sensor_info) is tuple:
                    # probably a two-tuple with a sensor ID and a substitute label
                    if len(sensor_info) != 2:
                        raise ValueError(f'Bad sensor ID / label format {sensor_info}')
                    sensor_id_list.append(sensor_info[0])
                    sensor_labels[sensor_info[0]] = sensor_info[1]
                else:
                    raise ValueError(f'Bad sensor ID format: {sensor_info}')

        # make a parameter dictionary, only including the parameters that
        # are not None.
        params = {}
        for pm in ('start_ts', 'end_ts', 'timezone', 'averaging', 'label_offset'):
            if locals()[pm] is not None:
                params[pm] = locals()[pm]
        # add the sensor ID list to the parameters
        params['sensor_id'] = sensor_id_list

        # make the API call
        resp = requests.get(self._url('api/v2/readings/'), params=params).json()

        # check for errors
        check_response(resp)

        df = pd.DataFrame(**resp['data']['readings'])
        df.index = pd.to_datetime(df.index)
        df.rename(columns=sensor_labels, inplace=True)
        # add an attribute that holds the timezone name
        df.bmon_timezone = resp['data']['reading_timezone']

        return df

    def sensors(self, sensor_ids=[]):
        """Returns properties of one or more requested sensors.

        Parameters:
            sensor_ids: A list of the sensor IDs for the requested sensors. If an empty list
                is passed (the default value), all sensors are returned.  Or, one
                sensor ID, not in a list, can be provided to request information for one
                sensor. (These are the string Sensor IDs that are discoverable by hovering
                the mouse over the sensor in the BMON Current Values report.)

        Returns:
            A list of dictionaries, each dicionary describing one sensor.  The dictionaries
            contain most or all of the fields of information describing the sensor, along with
            information about the buildings associated with the sensor.
        """
        params = {'sensor_id': sensor_ids}
        # make the API call
        resp = requests.get(self._url('api/v2/sensors/'), params=params).json()

        check_response(resp)
        return resp['data']['sensors']

    def buildings(self, building_ids=[]):
        """Returns properties of one or more requested buildings.

        Parameters:
            building_ids: A list of the building IDs for the requested buildings. An empty list
                returns all buildings.  Also, one building ID, not in a list, can be provided to
                request information for one building.

        Returns:
            A list of dictionaries, each dicionary describing one building.  The dictionaries
            contain most or all of the fields of information describing the building, along with
            information about the sensors and organizations associated with the building.
        """
        params = {'building_id': building_ids}
        # make the API call
        resp = requests.get(self._url('api/v2/buildings/'), params=params).json()

        check_response(resp)
        return resp['data']['buildings']

    def organizations(self, organization_ids=[]):
        """Returns properties of one or more requested organizations.

        Parameters:
            organization_ids: A list of the organization IDs for the requested sensors. An empty
                list will return all organizations.  Also, one sensor ID, not in a list, can be 
                provided to request information for one organization.

        Returns:
            A list of dictionaries, each dicionary describing one organization.  The dictionaries
            contain most or all of the fields of information describing the organization, along with
            information about the buildings associated with the organization.
        """
        params = {'organization_id': organization_ids}
        # make the API call
        resp = requests.get(self._url('api/v2/organizations/'), params=params).json()

        check_response(resp)
        return resp['data']['organizations']

    def store_sensor_readings(self, reading_list):
        """This method will store the sensor readings in 'reading_list' in the BMON sensor
        reading database.  Note that the BMON server's 'store_key' must be passed into the
        constructor of the Server object for this method to function.

        Parameters:
            reading_list: A list of sensor readings; each sensor reading is in turn a 3-item
                list or tuple of the form:  (UNIX epoch timestamp, Sensor ID, reading value).
                An example reading_list is:
                    [
                        (142343232, 'abc_sensor', 23.4),
                        (142343235, 'xyz_sensor', 18.8)
                    ]
        
        Returns: the number of sensor readings successfully stored.
        """

        if self.store_key is None:
            raise ValueError('No "store_key" present. The Server object must be constructed with a "store_key".')

        # make the Post parameter necessary to store the readings on BMON
        post_data = json.dumps(
            {
                'storeKey': self.store_key,
                'readings': reading_list
            }
        )

        resp = requests.post(self._url('readingdb/reading/store/'), data=post_data, timeout=15, verify=False).text
        match = re.match(r'(\d+) readings stored successfully', resp)
        if match:
            return(int(match.groups()[0]))
        else:
            raise ValueError(f'Error storing readings: {resp}')
