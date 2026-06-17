"""Smart Oil Gauge API client."""
import logging
import re
import json
import async_timeout

_LOGGER = logging.getLogger(__name__)

LOGIN_URL = "https://app.smartoilgauge.com/login.php"
BASE_URL = "https://app.smartoilgauge.com/ajax/main_ajax.php"


class SmartOilGaugeClient:
    """Client for the Smart Oil Gauge / Connected Consumer Fuel API."""

    def __init__(self, username: str, password: str, session):
        self._username = username
        self._password = password
        self._session = session
        self._phpsessid = None

    async def login(self) -> bool:
        """Log in and obtain a session cookie."""
        try:
            async with async_timeout.timeout(15):
                # Fetch login page to get CSRF nonce and initial session cookie
                get_resp = await self._session.get(LOGIN_URL)
                html = await get_resp.text()

                nonce_match = re.search(
                    r"ccf_nonce[^>]+value=['\"]([^'\"]+)['\"]"
                    r"|value=['\"]([^'\"]+)['\"][^>]+ccf_nonce",
                    html,
                )
                if not nonce_match:
                    _LOGGER.error("Smart Oil Gauge: could not find login nonce")
                    return False
                nonce = nonce_match.group(1) or nonce_match.group(2)

                phpsessid = get_resp.cookies.get("PHPSESSID")
                if phpsessid:
                    self._phpsessid = phpsessid.value.strip('"')

                await self._session.post(
                    LOGIN_URL,
                    data={
                        "username": self._username,
                        "user_pass": self._password,
                        "ccf_nonce": nonce,
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Referer": LOGIN_URL,
                        "Origin": "https://app.smartoilgauge.com",
                    },
                    cookies={"PHPSESSID": self._phpsessid} if self._phpsessid else {},
                    allow_redirects=True,
                )

                # Update session cookie after login
                for cookie in self._session.cookie_jar:
                    if cookie.key == "PHPSESSID":
                        self._phpsessid = cookie.value.strip('"')
                        break

                # Verify login succeeded by fetching tanks
                tanks = await self._fetch_tanks()
                if tanks is None:
                    _LOGGER.error("Smart Oil Gauge: login verification failed")
                    return False
                return True

        except Exception as err:
            _LOGGER.error("Smart Oil Gauge: login error: %s", err)
            return False

    async def _fetch_tanks(self):
        """Fetch tank data from the API."""
        try:
            async with async_timeout.timeout(15):
                resp = await self._session.post(
                    BASE_URL,
                    data={"action": "get_tanks_list", "tank_id": "0"},
                    headers={
                        "Referer": "https://app.smartoilgauge.com/app.php",
                        "Origin": "https://app.smartoilgauge.com",
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    cookies={"PHPSESSID": self._phpsessid.strip('"')} if self._phpsessid else {},
                )
                text = await resp.text()
                data = json.loads(text)
                if data.get("result") == "ok":
                    return data.get("tanks", [])
                return None
        except Exception as err:
            _LOGGER.error("Smart Oil Gauge: fetch error: %s", err)
            return None

    async def get_tanks(self) -> list:
        """Get tank data, re-logging in if the session has expired."""
        tanks = await self._fetch_tanks()
        if tanks is None:
            _LOGGER.debug("Smart Oil Gauge: session expired, re-logging in")
            if await self.login():
                tanks = await self._fetch_tanks()
        return tanks or []
