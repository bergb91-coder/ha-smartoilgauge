"""Config flow for Smart Oil Gauge."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import SmartOilGaugeClient
from .const import DOMAIN

DATA_SCHEMA = vol.Schema({
    vol.Required("username"): str,
    vol.Required("password"): str,
})


class SmartOilGaugeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Oil Gauge."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = SmartOilGaugeClient(
                user_input["username"], user_input["password"], session
            )
            if await client.login():
                return self.async_create_entry(
                    title="Smart Oil Gauge",
                    data=user_input,
                )
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
