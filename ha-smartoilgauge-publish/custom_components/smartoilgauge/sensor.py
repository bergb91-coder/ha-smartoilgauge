"""Sensor platform for Smart Oil Gauge."""
import logging
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Smart Oil Gauge sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for tank in coordinator.data:
        tank_id = tank["tank_id"]
        tank_name = tank["tank_name"]
        entities += [
            SmartOilGaugeLevelSensor(coordinator, tank_id, tank_name),
            SmartOilGaugePercentSensor(coordinator, tank_id, tank_name),
            SmartOilGaugeBatterySensor(coordinator, tank_id, tank_name),
            SmartOilGaugeLastReadSensor(coordinator, tank_id, tank_name),
        ]
    async_add_entities(entities)


class SmartOilGaugeBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Smart Oil Gauge sensors."""

    def __init__(self, coordinator, tank_id: str, tank_name: str):
        super().__init__(coordinator)
        self._tank_id = tank_id
        self._tank_name = tank_name

    def _get_tank(self) -> dict:
        for tank in self.coordinator.data:
            if tank["tank_id"] == self._tank_id:
                return tank
        return {}

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._tank_id)},
            "name": f"Smart Oil Gauge – {self._tank_name}",
            "manufacturer": "Connected Consumer Fuel",
            "model": "Smart Oil Gauge",
        }


class SmartOilGaugeLevelSensor(SmartOilGaugeBaseSensor):
    """Sensor reporting gallons remaining in the tank."""

    @property
    def unique_id(self):
        return f"smartoilgauge_{self._tank_id}_gallons"

    @property
    def name(self):
        return f"{self._tank_name} Oil Level"

    @property
    def native_value(self):
        val = self._get_tank().get("sensor_gallons")
        try:
            return round(float(val), 1) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def native_unit_of_measurement(self):
        return "gal"

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        return "mdi:gauge"

    @property
    def extra_state_attributes(self):
        tank = self._get_tank()
        nominal = tank.get("nominal")
        gallons = tank.get("sensor_gallons")
        pct = None
        if nominal and gallons:
            try:
                pct = round((float(gallons) / float(nominal)) * 100, 1)
            except (ValueError, TypeError):
                pass
        return {
            "tank_capacity_gal": nominal,
            "fill_percent": pct,
            "tank_name": tank.get("tank_name"),
            "sensor_status": tank.get("sensor_status"),
            "last_read": tank.get("sensor_rt"),
            "battery": tank.get("battery"),
        }


class SmartOilGaugePercentSensor(SmartOilGaugeBaseSensor):
    """Sensor reporting tank fill percentage."""

    @property
    def unique_id(self):
        return f"smartoilgauge_{self._tank_id}_percent"

    @property
    def name(self):
        return f"{self._tank_name} Oil Percent"

    @property
    def native_value(self):
        tank = self._get_tank()
        nominal = tank.get("nominal")
        gallons = tank.get("sensor_gallons")
        try:
            if nominal and gallons:
                return round((float(gallons) / float(nominal)) * 100, 1)
        except (ValueError, TypeError):
            pass
        return None

    @property
    def native_unit_of_measurement(self):
        return "%"

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        return "mdi:percent"


class SmartOilGaugeBatterySensor(SmartOilGaugeBaseSensor):
    """Sensor reporting gauge battery health."""

    @property
    def unique_id(self):
        return f"smartoilgauge_{self._tank_id}_battery"

    @property
    def name(self):
        return f"{self._tank_name} Oil Gauge Battery"

    @property
    def native_value(self):
        return self._get_tank().get("battery")

    @property
    def icon(self):
        val = (self._get_tank().get("battery") or "").lower()
        if val == "good":
            return "mdi:battery"
        if val == "ok":
            return "mdi:battery-50"
        return "mdi:battery-alert"


class SmartOilGaugeLastReadSensor(SmartOilGaugeBaseSensor):
    """Sensor reporting the last time the gauge uploaded a reading."""

    @property
    def unique_id(self):
        return f"smartoilgauge_{self._tank_id}_last_read"

    @property
    def name(self):
        return f"{self._tank_name} Oil Gauge Last Read"

    @property
    def native_value(self):
        return self._get_tank().get("sensor_rt")

    @property
    def icon(self):
        return "mdi:clock-outline"
