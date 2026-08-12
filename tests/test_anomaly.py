from app.anomaly import check_reading


def test_normal_reading_is_ok():
    result = check_reading(temperature_c=65.0, vibration_mm_s=2.0, pressure_bar=8.0)
    assert result["status"] == "ok"
    assert result["reasons"] == []


def test_high_temperature_is_warning():
    result = check_reading(temperature_c=85.0, vibration_mm_s=2.0, pressure_bar=8.0)
    assert result["status"] == "warning"


def test_critical_temperature_is_critical():
    result = check_reading(temperature_c=97.0, vibration_mm_s=2.0, pressure_bar=8.0)
    assert result["status"] == "critical"


def test_high_vibration_is_warning():
    result = check_reading(temperature_c=65.0, vibration_mm_s=5.0, pressure_bar=8.0)
    assert result["status"] == "warning"


def test_critical_vibration_is_critical():
    result = check_reading(temperature_c=65.0, vibration_mm_s=8.0, pressure_bar=8.0)
    assert result["status"] == "critical"


def test_low_pressure_is_critical():
    # Loss of discharge pressure can mean cavitation — must never be missed.
    result = check_reading(temperature_c=65.0, vibration_mm_s=2.0, pressure_bar=1.5)
    assert result["status"] == "critical"


def test_worst_level_wins():
    result = check_reading(temperature_c=85.0, vibration_mm_s=8.0, pressure_bar=8.0)
    assert result["status"] == "critical"
    assert len(result["reasons"]) == 2
