# Aquilo for Home Assistant

A custom [Home Assistant](https://www.home-assistant.io/) integration for
[Aquilo](https://www.aquilo.pl) level sensors. It polls the device's local
`/state` HTTP endpoint and creates a proper **device** with sensor entities —
no YAML, no template hacks.

> This is an unofficial, community-built integration. The author is not
> affiliated with Aquilo.

## Features

- Local polling — no cloud, no account required.
- UI config flow (just enter the device IP/hostname).
- One Home Assistant **device per sensor** reported by the endpoint
  (the `/state` response can list several under `sensors[]`).
- Entities with correct device classes, units and long-term statistics:

  | Entity | Source field | Unit | Notes |
  | --- | --- | --- | --- |
  | Level | `lvl` | cm | `measurement` |
  | Percent full | `pct` | % | `measurement` |
  | Battery | `bat` | % | `device_class: battery` |
  | Days left | `daysLeft` | d | |
  | Distance to full | `lvlToFull` | cm | disabled by default |
  | Last read | `lstRead` | — | `device_class: timestamp` (shows "x ago") |
  | Last emptied | `lstEmpty` | — | `device_class: timestamp` |

- Polling interval defaults to **15 minutes** (the device refreshes on its own
  schedule) and is adjustable via the integration's **Configure** button.

## Installation

### HACS (custom repository)

1. HACS → ⋮ → **Custom repositories**.
2. Add `https://github.com/nb3rt/Aquilo-HomeAssistant-HACS` with category **Integration**.
3. Install **Aquilo**, then restart Home Assistant.

### Manual

Copy `custom_components/aquilo` into your Home Assistant `config/custom_components/`
directory and restart.

## Configuration

**Settings → Devices & Services → Add Integration → Aquilo**, then enter the
device's IP address or hostname (e.g. `192.168.1.246`).

To change the polling interval later: open the integration and click
**Configure**.

## Example dashboard (Sections view)

The integration ships only entities; the dashboard below is an example you can
copy. Paste it as the YAML of a new **Sections** view. Adjust the `entity_id`s
to match what was created (check **Developer Tools → States**).

```yaml
type: sections
title: Aquilo
path: aquilo
icon: mdi:water-well
sections:
  - type: grid
    cards:
      - type: heading
        heading: Aquilo
        heading_style: title
        icon: mdi:water-well

      - type: gauge
        entity: sensor.aquilo_percent_full
        name: Zapełnienie
        unit: "%"
        min: 0
        max: 100
        needle: true
        severity:
          green: 0
          yellow: 60
          red: 85
        grid_options:
          columns: full

      - type: tile
        entity: sensor.aquilo_level
        name: Poziom
        icon: mdi:waves
        color: cyan

      - type: tile
        entity: sensor.aquilo_days_left
        name: Dni do pełna
        icon: mdi:calendar-clock
        color: amber

      - type: tile
        entity: sensor.aquilo_battery
        name: Bateria
        icon: mdi:battery

  - type: grid
    cards:
      - type: heading
        heading: Historia odczytów
        heading_style: subtitle
        icon: mdi:history

      - type: tile
        entity: sensor.aquilo_last_read
        name: Ostatni odczyt
        icon: mdi:clock-outline
        color: blue
        state_content: relative

      - type: tile
        entity: sensor.aquilo_last_emptied
        name: Ostatnie opróżnienie
        icon: mdi:delete-clock-outline
        color: orange

      - type: history-graph
        title: Zapełnienie i poziom (14 dni)
        hours_to_show: 336
        entities:
          - entity: sensor.aquilo_percent_full
            name: Zapełnienie
          - entity: sensor.aquilo_level
            name: Poziom
        grid_options:
          columns: full
```

> "Time since last read" is intentionally **not** a separate entity — the
> *Last read* tile already shows an adaptive relative time ("5 min ago",
> "3 days ago") thanks to its `timestamp` device class.

## Notes / limitations

- New sensor ids that appear *after* setup require an integration reload to be
  picked up (Settings → Devices & Services → Aquilo → Reload).
- The integration assumes the device is reachable over plain HTTP on the local
  network.

## License

[MIT](LICENSE)
