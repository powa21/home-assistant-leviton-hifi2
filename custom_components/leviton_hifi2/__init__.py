from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .protocol import HifiClient

PLATFORMS = ["media_player", "light"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = HifiClient(hass, entry.data["host"], entry.data["port"], entry.data["zones"])
    await client.start()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True

async def async_update_options(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        client = hass.data[DOMAIN].pop(entry.entry_id)
        await client.stop()
    return ok
