"""Local TCP implementation of Leviton Hi-Fi 2 ASCII command protocol."""
import asyncio
import logging
import re
from collections import defaultdict
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
RE_ZONE = re.compile(r'^#Z(\d+)(POWER|VOLUME|MUTE|SRC|NAME)(.*)$', re.I)
RE_SOURCE = re.compile(r'^#S(\d+)NAME"(.*)"$', re.I)

class HifiClient:
    def __init__(self, hass, host, port, zones):
        self.hass, self.host, self.port, self.zones = hass, host, port, zones
        self.states = defaultdict(dict)
        self.sources = {i: f"Source {i}" for i in range(1, 9)}
        self.connected = False
        self._task = None
        self._writer = None
        self._lock = asyncio.Lock()
        self._last_sent = 0.0
        self._closing = False

    @property
    def signal(self):
        return f"{DOMAIN}_{self.host}_{self.port}"

    async def start(self):
        self._task = self.hass.async_create_background_task(self._run(), f"{DOMAIN}_tcp", eager_start=False)

    async def stop(self):
        self._closing = True
        if self._writer:
            self._writer.close()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def send(self, command):
        if not self.connected or not self._writer:
            raise ConnectionError("Hi-Fi 2 is not connected")
        if not re.fullmatch(r"\*[A-Za-z0-9?+\-]+", command):
            raise ValueError("Invalid command")
        async with self._lock:
            loop = asyncio.get_running_loop()
            await asyncio.sleep(max(0, 0.05 - (loop.time() - self._last_sent)))
            self._writer.write((command + "\r").encode("ascii"))
            await self._writer.drain()
            self._last_sent = loop.time()

    async def _refresh(self):
        for s in range(1, 9):
            await self.send(f"*S{s}NAME?")
        for z in range(1, self.zones + 1):
            for attr in ("NAME", "POWER", "VOLUME", "MUTE", "SRC"):
                await self.send(f"*Z{z}{attr}?")

    async def _run(self):
        while not self._closing:
            try:
                reader, self._writer = await asyncio.open_connection(self.host, self.port)
                self.connected = True
                async_dispatcher_send(self.hass, self.signal)
                await self._refresh()
                while not self._closing:
                    raw = await reader.readline()
                    if not raw:
                        break
                    line = raw.decode("utf-8", "replace").strip()
                    self._parse(line)
            except asyncio.CancelledError:
                raise
            except (OSError, ConnectionError) as exc:
                _LOGGER.warning("Hi-Fi 2 connection issue: %s", exc)
            finally:
                self.connected = False
                async_dispatcher_send(self.hass, self.signal)
                if self._writer:
                    self._writer.close()
                    self._writer = None
            if not self._closing:
                await asyncio.sleep(5)

    def _parse(self, line):
        if line.startswith("#?"):
            _LOGGER.warning("Hi-Fi 2 rejected command: %s", line)
            return
        m = RE_SOURCE.fullmatch(line)
        if m:
            self.sources[int(m.group(1))] = m.group(2)
            async_dispatcher_send(self.hass, self.signal)
            return
        m = RE_ZONE.fullmatch(line)
        if not m:
            return
        zone, key, val = int(m.group(1)), m.group(2).upper(), m.group(3)
        if key == "NAME":
            val = val.strip('"')
        else:
            try:
                val = int(val)
            except ValueError:
                return
        self.states[zone][key] = val
        async_dispatcher_send(self.hass, self.signal)
