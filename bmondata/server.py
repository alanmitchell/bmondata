from urllib.parse import urljoin
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

    def __init__(self, base_url):

        # make a call to the server to see if it is accessible
        # make store-key method has been around since the beginning.
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
        """
        """
        params = {'sensor_id': sensor_ids}
        # make the API call
        resp = requests.get(self._url('api/v2/sensors/'), params=params).json()

        check_response(resp)
        return resp['data']['sensors']

    def buildings(self, building_ids=[]):
        """
        """
        params = {'building_id': building_ids}
        # make the API call
        resp = requests.get(self._url('api/v2/buildings/'), params=params).json()

        check_response(resp)
        return resp['data']['buildings']

    def organizations(self, organization_ids=[]):
        """
        """
        params = {'organization_id': organization_ids}
        # make the API call
        resp = requests.get(self._url('api/v2/organizations/'), params=params).json()

        check_response(resp)
        return resp['data']['organizations']
