import re
import requests
import json
import time
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.const import (TEMP_CELSIUS,CONF_NAME,ATTR_TIME,ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.util import Throttle

from datetime import datetime
from datetime import timedelta

_Log=logging.getLogger(__name__)

MOJI_URL = 'moji_url'
DEFAULT_NAME = 'mojiAir'
ATTRIBUTION = 'Data provided by the MOJI Air Quality Device'

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(MOJI_URL): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    host = config.get(MOJI_URL)
    if host == None:
        _Log.error('Pls enter url!')
    name = config.get(CONF_NAME)
    gateway = mojiGateway(host)
    gateway.update()

    dev = []
    for mtu in gateway.data:
        dev.append(mojiAir(gateway, name,'PM25', mtu, 'μg/m3', 'mdi:cloud'))  #PM2.5
        dev.append(mojiAir(gateway, name,'HCHO', mtu, 'μg/m3', 'mdi:chemical-weapon'))    #HCHO
        dev.append(mojiAir(gateway, name,'TEMP', mtu, '°C', 'mdi:thermometer'))    #TEMP
        dev.append(mojiAir(gateway, name,'HUMI', mtu, '%', 'mdi:water-percent'))    #HUMI
       # dev.append(mojiAir(gateway, name,'PM25_DESC', mtu, None, 'mdi:cloud-print'))    #PM25 DESC
       # dev.append(mojiAir(gateway, name,'HCHO_DESC', mtu, None, 'mdi:tag-text-outline'))    #HCHO DESC
       # dev.append(mojiAir(gateway, name,'TEMP_DESC', mtu, None, 'mdi:tag-multiple'))    #TEMP DESC
       # dev.append(mojiAir(gateway, name,'HUMI_DESC', mtu, None, 'mdi:tag-outline'))    #HUMI DESC

    add_devices(dev,True)
    #return True


class mojiAir(Entity):
    """Representation of a Sensor."""

    def __init__(self, gateway, name,keyname, mtu, unit, icon):
        """Initialize the sensor."""
        self._gateway = gateway
        self._name = '{}_{}_{}'.format(name, mtu, keyname)
        self._keyname = keyname
        self._mtu = mtu
        self._unit = unit
        self._icon = icon
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit

    @property
    def icon(self):
        """Return the unit the value is expressed in."""
        return self._icon

    @property
    def state(self):
        """Return the state of the resources."""
        try:
            return self._gateway.data[self._mtu][self._keyname]
        except KeyError:
            pass

    @property
    def device_state_attributes(self):
        """Return the state attributes of the last update."""
        attrs = {}

        if self._gateway.data[self._mtu] is not None:
            try:
                attrs[ATTR_TIME] = self._gateway.data[self._mtu]['TIME']
                attrs['description'] = self._gateway.data[self._mtu]['{}_DESC'.format(self._keyname)]
                return attrs
            except (IndexError, KeyError):
                return {ATTR_ATTRIBUTION: ATTRIBUTION}

    def update(self):
        """Get the latest data from REST API."""
        self._gateway.update()

class mojiGateway(object):
    """The class for handling the data retrieval."""

    def __init__(self, host):
        """Initialize the data object."""
        self.host = host
        self.data = dict()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        if self.host == '':
            _Log.error("[MOJI]: url is nil")
            return
        api_url = self.host
        resp = requests.get(api_url)
        if resp.status_code != 200:
            _Log.error("[MOJI]: http get error code --" + resp.status_code)
            return
        resp.encoding = "utf-8"
        s = resp.text
        #_Log.error(s)
        datas = json.loads(s)
        time_local = time.localtime(datas['result'][0]['datas']['detectTime'] / 1000)
        dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
        DETECT = dt
        HCHO = float('%.1f' % (datas['result'][0]['datas']['hcho'] * 1000))
        HCHO_DESC = datas['result'][0]['datas']['hchoDesc']
        TEMP = datas['result'][0]['datas']['temp']
        TEMP_DESC = datas['result'][0]['datas']['tempDesc']
        HUMI = datas['result'][0]['datas']['humidity']
        #self.attributes['HUMI_DESC'] = datas['result'][0]['datas']['humidityDesc']
        HUMI_DESC = datas['result'][0]['datas']['humidityDesc']
        PM25 = datas['result'][0]['datas']['pm25']
        PM25_DESC = datas['result'][0]['datas']['pm25Desc']
        self.data[0] = {'PM25': PM25, 'HCHO': HCHO, 'TEMP': TEMP, 'HUMI': HUMI, 'PM25_DESC': PM25_DESC, 'HCHO_DESC': HCHO_DESC, 'TEMP_DESC': TEMP_DESC, 'HUMI_DESC': HUMI_DESC,'TIME': dt}





