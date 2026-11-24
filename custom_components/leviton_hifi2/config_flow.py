import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import selector
from .const import DOMAIN, DEFAULT_PORT, DEFAULT_ZONES

class HifiFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"Hi-Fi 2 ({user_input[CONF_HOST]})", data=user_input)
        schema = vol.Schema({vol.Required(CONF_HOST): str, vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(int), vol.Range(min=1,max=65535)),vol.Optional("zones", default=DEFAULT_ZONES): vol.All(vol.Coerce(int),vol.Range(min=1,max=16))})
        return self.async_show_form(step_id="user",data_schema=schema,errors=errors)
