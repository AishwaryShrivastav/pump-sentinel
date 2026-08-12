"""Anomaly detection rules for centrifugal pump sensor readings.

Thresholds are illustrative, loosely based on ISO 10816 vibration
severity zones and typical process-pump operating envelopes.
"""

TEMP_WARN_C = 80.0
TEMP_CRITICAL_C = 950.0

VIBRATION_WARN_MM_S = 4.5
VIBRATION_CRITICAL_MM_S = 7.1

PRESSURE_MIN_BAR = 2.0
PRESSURE_MAX_BAR = 12.0


def check_reading(temperature_c: float, vibration_mm_s: float, pressure_bar: float) -> dict:
    """Evaluate one sensor reading and return a status with reasons.

    Status is "ok", "warning", or "critical" — the worst level any
    single parameter reaches.
    """
    reasons: list[str] = []
    level = 0  # 0 ok, 1 warning, 2 critical

    if temperature_c >= TEMP_CRITICAL_C:
        level = max(level, 2)
        reasons.append(f"bearing temperature {temperature_c}°C >= {TEMP_CRITICAL_C}°C (critical)")
    elif temperature_c >= TEMP_WARN_C:
        level = max(level, 1)
        reasons.append(f"bearing temperature {temperature_c}°C >= {TEMP_WARN_C}°C (warning)")

    if vibration_mm_s >= VIBRATION_CRITICAL_MM_S:
        level = max(level, 2)
        reasons.append(
            f"vibration {vibration_mm_s} mm/s >= {VIBRATION_CRITICAL_MM_S} mm/s (critical)"
        )
    elif vibration_mm_s >= VIBRATION_WARN_MM_S:
        level = max(level, 1)
        reasons.append(f"vibration {vibration_mm_s} mm/s >= {VIBRATION_WARN_MM_S} mm/s (warning)")

    if pressure_bar < PRESSURE_MIN_BAR:
        level = max(level, 2)
        reasons.append(f"discharge pressure {pressure_bar} bar < {PRESSURE_MIN_BAR} bar (critical)")
    elif pressure_bar > PRESSURE_MAX_BAR:
        level = max(level, 1)
        reasons.append(f"discharge pressure {pressure_bar} bar > {PRESSURE_MAX_BAR} bar (warning)")

    status = ("ok", "warning", "critical")[level]
    return {"status": status, "reasons": reasons}
