"""Optional-to-enable virtual dimmers for Apple Home volume control."""
from homeassistant.components.light import LightEntity, ColorMode, ATTR_BRIGHTNESS
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HifiVolumeLight(client, z) for z in range(1, client.zones + 1)])

class HifiVolumeLight(LightEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_icon = 'mdi:volume-high'
    _attr_entity_registry_enabled_default = False

    def __init__(self, client, zone):
        self.client, self.zone = client, zone
        self._attr_unique_id = f'{client.host}_{client.port}_zone_{zone}_volume_light'
        self._attr_name = f'Zone {zone} Audio Volume'
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, f'{client.host}:{client.port}')}, name='Leviton Hi-Fi 2', manufacturer='Leviton', model='95A00-1')

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, self.client.signal, self.async_write_ha_state))

    @property
    def available(self):
        return self.client.connected and 'POWER' in self.client.states[self.zone]

    @property
    def is_on(self):
        value = self.client.states[self.zone].get('POWER')
        return None if value is None else bool(value)

    @property
    def brightness(self):
        value = self.client.states[self.zone].get('VOLUME')
        return None if value is None else max(1, min(255, round(value * 255 / 100)))

    async def async_turn_on(self, **kwargs):
        if ATTR_BRIGHTNESS in kwargs:
            level = max(1, min(100, round(kwargs[ATTR_BRIGHTNESS] * 100 / 255)))
            if not self.is_on:
                await self.client.send(f'*Z{self.zone}POWER1')
            await self.client.send(f'*Z{self.zone}VOLUME{level}')
        elif not self.is_on:
            await self.client.send(f'*Z{self.zone}POWER1')

    async def async_turn_off(self, **kwargs):
        await self.client.send(f'*Z{self.zone}POWER0')
