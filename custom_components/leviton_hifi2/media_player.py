from homeassistant.components.media_player import MediaPlayerDeviceClass, MediaPlayerEntity, MediaPlayerEntityFeature, MediaPlayerState
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HifiZone(client, z) for z in range(1, client.zones + 1)])

class HifiZone(MediaPlayerEntity):
    _attr_device_class = MediaPlayerDeviceClass.RECEIVER
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_supported_features = (MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF |
        MediaPlayerEntityFeature.VOLUME_SET | MediaPlayerEntityFeature.VOLUME_MUTE |
        MediaPlayerEntityFeature.SELECT_SOURCE)

    def __init__(self, client, zone):
        self.client, self.zone = client, zone
        self._attr_unique_id = f"{client.host}_{client.port}_zone_{zone}"
        self._attr_name = f"Zone {zone}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, f"{client.host}:{client.port}")}, name="Leviton Hi-Fi 2", manufacturer="Leviton", model="95A00-1")

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, self.client.signal, self.async_write_ha_state))

    @property
    def available(self):
        return self.client.connected

    @property
    def name(self):
        return self.client.states[self.zone].get("NAME") or self._attr_name

    @property
    def state(self):
        power = self.client.states[self.zone].get("POWER")
        if power is None:
            return None
        return MediaPlayerState.ON if power else MediaPlayerState.OFF

    @property
    def volume_level(self):
        value = self.client.states[self.zone].get("VOLUME")
        return value / 100 if value is not None else None

    @property
    def is_volume_muted(self):
        value = self.client.states[self.zone].get("MUTE")
        return bool(value) if value is not None else None

    @property
    def source(self):
        index = self.client.states[self.zone].get("SRC")
        return self.client.sources.get(index) if index else None

    @property
    def source_list(self):
        return [self.client.sources[i] for i in range(1, 9)]

    async def async_turn_on(self):
        await self.client.send(f"*Z{self.zone}POWER1")

    async def async_turn_off(self):
        await self.client.send(f"*Z{self.zone}POWER0")

    async def async_set_volume_level(self, volume):
        level = max(1, min(100, round(volume * 100)))
        await self.client.send(f"*Z{self.zone}VOLUME{level}")

    async def async_mute_volume(self, mute):
        await self.client.send(f"*Z{self.zone}MUTE{int(mute)}")

    async def async_select_source(self, source):
        matches = [i for i, name in self.client.sources.items() if name == source]
        if not matches:
            raise ValueError(f"Unknown source: {source}")
        await self.client.send(f"*Z{self.zone}SRC{matches[0]}")
