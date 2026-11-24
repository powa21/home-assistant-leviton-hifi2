# Leviton / HAI Hi-Fi 2 for Home Assistant

Community integration for legacy multiroom audio systems using local TCP control. Includes receiver and optional virtual dimmer controls. Independent project, not affiliated with Leviton or Home Assistant.

## Features
- Configurable 1–16 zones, eight sources, local TCP (default port 23).
- Receiver entities with power, volume, mute and source selection.
- Optional virtual dimmers for Apple Home volume control; disabled by default.
- Feedback from amplifier status messages, including wall controls.

## Compatibility
Developed for 95A00-1. Other models and 16-zone installations require community testing. The maintainer has confirmed successful live hardware testing. Other installations may vary.

## HACS installation
Install [HACS](https://www.hacs.xyz/). Open HACS, choose Custom repositories from the three-dot menu, paste `https://github.com/powa21/home-assistant-leviton-hifi2`, select Integration, and download. Restart Home Assistant. Under Settings → Devices & services → Add integration, search for Leviton Hi-Fi 2. Enter the amplifier IP address, TCP port (23 by default), and zone count. Keep the amplifier on a trusted local network; do not expose port 23 to the internet.

## Manual installation
Copy `custom_components/leviton_hifi2` into your Home Assistant `config/custom_components` directory and restart. Configure as above. For upgrades, back up the existing folder and replace it without deleting the integration. Entity IDs from earlier experimental versions may differ; back up before upgrading.

## Apple Home
Expose each receiver via an individual HomeKit Bridge in accessory mode for power and source selection. For volume, open Settings → Devices & services → Entities, include disabled entities, and enable each Zone N Audio Volume light. Add those lights to a separate standard HomeKit Bridge and pair it with Apple Home. Place the two accessories in the same room. Brightness maps to volume 1–100; turning off the light turns off the audio zone. Turning on may power on the zone. Start at low volume; 100% is maximum. Exclude virtual lights from lighting scenes, adaptive lighting and all-light automations.

## Troubleshooting
Check IP, port, network reachability and zone count. Check Settings → System → Logs for connection issues. Verify power, source, low-volume adjustments and physical controller feedback before enabling all zones. Roll back by restoring your backed-up driver and restarting. Remove any old `leviton_native_speaker.enabled` flag; this release does not include the experimental v0.4 HomeKit patch.

## Licence
MIT — see [LICENSE](LICENSE). Maintainer: [powa21](https://github.com/powa21).

## Feedback
Report reproducible issues through GitHub Issues, with Home Assistant version, amplifier model, steps and redacted logs. Never include passwords or public IP addresses.
