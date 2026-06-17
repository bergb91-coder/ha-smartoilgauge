"""Smart Oil Gauge integration for Home Assistant."""
from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import SmartOilGaugeClient
from .const import DOMAIN, SCAN_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Oil Gauge from a config entry."""
    session = async_get_clientsession(hass)
    client = SmartOilGaugeClient(
        entry.data["username"], entry.data["password"], session
    )

    if not await client.login():
        return False

    async def async_update_data():
        tanks = await client.get_tanks()
        if not tanks:
            raise UpdateFailed("Failed to fetch tank data from Smart Oil Gauge")
        return tanks

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="smartoilgauge",
        update_method=async_update_data,
        update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Smart Oil Gauge config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
