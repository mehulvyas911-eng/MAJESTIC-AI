import pytest
from visual_engine import severity_card, SEV_CRITICAL, SEV_HIGH, SEV_MEDIUM, SEV_LOW, SEV_INFO

def test_severity_card_critical():
    result = severity_card("Critical Title", "critical", "Critical Details")
    assert "CRITICAL" in result
    assert "Critical Title" in result
    assert "Critical Details" in result
    assert SEV_CRITICAL in result

def test_severity_card_high():
    result = severity_card("High Title", "high", "High Details")
    assert "HIGH" in result
    assert "High Title" in result
    assert "High Details" in result
    assert SEV_HIGH in result

def test_severity_card_medium():
    result = severity_card("Medium Title", "medium", "Medium Details")
    assert "MEDIUM" in result
    assert "Medium Title" in result
    assert "Medium Details" in result
    assert SEV_MEDIUM in result

def test_severity_card_low():
    result = severity_card("Low Title", "low", "Low Details")
    assert "LOW" in result
    assert "Low Title" in result
    assert "Low Details" in result
    assert SEV_LOW in result

def test_severity_card_info():
    result = severity_card("Info Title", "info", "Info Details")
    assert "INFO" in result
    assert "Info Title" in result
    assert "Info Details" in result
    assert SEV_INFO in result

def test_severity_card_unknown():
    result = severity_card("Unknown Title", "unknown", "Unknown Details")
    assert "UNKNOWN" in result
    assert "Unknown Title" in result
    assert "Unknown Details" in result
    # It should fallback to SEV_INFO colors
    assert SEV_INFO in result

def test_severity_card_case_insensitivity():
    result = severity_card("Case Title", "CrItIcAl", "Case Details")
    assert "CRITICAL" in result
    assert SEV_CRITICAL in result

def test_severity_card_empty_detail():
    result = severity_card("Title", "info", "")
    assert "INFO" in result
    assert "Title" in result
