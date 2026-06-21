"""Constants for the Aquilo integration."""

from __future__ import annotations

DOMAIN = "aquilo"

MANUFACTURER = "Aquilo"
MODEL = "Aquilo level sensor"

# The device refreshes its own readings on its own schedule, so polling it
# more often than every few minutes gains nothing. Default to 15 minutes.
DEFAULT_SCAN_INTERVAL = 900  # seconds
MIN_SCAN_INTERVAL = 60  # seconds

REQUEST_TIMEOUT = 10  # seconds
