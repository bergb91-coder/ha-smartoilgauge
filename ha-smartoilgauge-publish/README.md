# Smart Oil Gauge — Home Assistant Integration

A Home Assistant custom integration for the [Smart Oil Gauge](https://www.smartoilgauge.com/) (Connected Consumer Fuel) heating oil tank monitor.

**No API subscription required** — uses your existing smartoilgauge.com account credentials.

---

## What it does

Creates sensors in Home Assistant for each tank on your account:

| Sensor | Description |
|---|---|
| `Oil Level` | Gallons remaining |
| `Oil Percent` | Fill percentage |
| `Oil Gauge Battery` | Battery health (Good / Ok / Poor) |
| `Oil Gauge Last Read` | Timestamp of last sensor upload |

The `Oil Level` sensor also exposes the following attributes:
- `tank_capacity_gal` — total tank capacity
- `fill_percent` — fill percentage
- `sensor_status` — sensor status (Active / Quiet / Offline)
- `last_read` — last reading timestamp
- `battery` — battery health

---

## Installation

### Via HACS (recommended)

1. In HACS go to **Integrations** → three dots → **Custom repositories**
2. Add `https://github.com/YOUR_GITHUB_USERNAME/ha-smartoilgauge` as an **Integration**
3. Click **Smart Oil Gauge** → **Download**
4. Restart Home Assistant
5. Go to **Settings → Devices & Services → Add Integration** → search **Smart Oil Gauge**
6. Enter your smartoilgauge.com email and password

### Manual

1. Copy the `custom_components/smartoilgauge` folder into your HA `custom_components` directory
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration** → search **Smart Oil Gauge**
4. Enter your smartoilgauge.com email and password

---

## Requirements

- A [Smart Oil Gauge](https://www.smartoilgauge.com/) device installed on your oil tank
- A smartoilgauge.com account
- Home Assistant 2023.1 or newer

---

## Notes

- Data updates every **60 minutes** (oil level doesn't change quickly)
- The integration uses your existing account login — no API key or subscription needed
- If your gauge battery is low (Poor), replace with **Saft LS14500 3.6V lithium AA** batteries

---

## Troubleshooting

**Invalid auth error on setup:** Double-check your email and password at [app.smartoilgauge.com](https://app.smartoilgauge.com). Make sure you're using the email address, not a username.

**Sensor shows old data:** Your gauge battery may be dead or the gauge may have lost WiFi. Check the `Oil Gauge Last Read` and `Oil Gauge Battery` sensors.

---

## Contributing

Issues and PRs welcome. This integration was reverse-engineered from the Smart Oil Gauge web app — if anything breaks after a site update please open an issue.

---

## License

MIT
