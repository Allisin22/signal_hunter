from signal_hunter import (
  find_peak,
  inspect_peak,
  calculate_responses,
  find_duplicate_frequencies,
  load_sweep,
)

def test_find_peak():
  responses = [
    {"trial_id": "T001", "frequency_hz": 100.0, "response": 0.002},
    {"trial_id": "T002", "frequency_hz": 200.0, "response": 0.009},
    {"trial_id": "T003", "frequency_hz": 300.0, "response": 0.004}
  ]

  peak = find_peak(responses)

  assert peak["trial_id"] == "T002"

def test_peak_at_boundary():
  responses = [
    {"trial_id": "T001", "frequency_hz": 100.0, "response": 0.002},
    {"trial_id": "T002", "frequency_hz": 200.0, "response": 0.004},
    {"trial_id": "T003", "frequency_hz": 300.0, "response": 0.009}
  ]

  peak = find_peak(responses)
  finding = inspect_peak(responses, peak)

  assert finding == "Peak is at the sweep boundary; cannot inspect both sides."

def test_peak_with_equal_neighbor():
  responses = [
    {"trial_id": "T001", "frequency_hz": 100.0, "response": 0.002},
    {"trial_id": "T002", "frequency_hz": 200.0, "response": 0.009},
    {"trial_id": "T003", "frequency_hz": 300.0, "response": 0.009}
  ]

  peak = find_peak(responses)
  finding = inspect_peak(responses, peak)

  assert finding == "the peak is not strictly higher than both immediate neighbors."

def test_zero_voltage_is_skipped():
  records = [
    {"trial_id": "T001", "frequency_hz": 100.0, "current": 0.01, "voltage": 0},
    {"trial_id": "T002", "frequency_hz": 200.0, "current": 0.02, "voltage": 5.0}
  ]

  responses, rejected_records = calculate_responses(records)

  assert len(responses) == 1
  assert responses[0]["trial_id"] == "T002"

def test_all_zero_voltages():
  records = [
    {"trial_id": "T001", "frequency_hz": 100.0, "current": 0.01, "voltage": 0},
    {"trial_id": "T002", "frequency_hz": 200.0, "current": 0.02, "voltage": 0}
  ]

  responses, rejected_records = calculate_responses(records)

  assert responses == []
  assert len(responses) == 0

def test_invalid_numeric_values_are_skipped():
  records = [
    {"trial_id": "T001", "frequency_hz": 100.0, "current": "hello", "voltage": 5.0},
    {"trial_id": "T002", "frequency_hz": 200.0, "current": True, "voltage": 5.0},
    {"trial_id": "T003", "frequency_hz": 300.0, "current": 0.019, "voltage": 5.0}
  ]

  responses, rejected_records  = calculate_responses(records)

  assert len(responses) == 1
  assert responses[0]["trial_id"] == "T003"

def test_missing_current_is_skipped():
  records = [
    {"trial_id": "T001", "frequency_hz": 100.0, "voltage": 5.0},
    {"trial_id": "T002", "frequency_hz": 200.0, "current": 0.02, "voltage": 5.0}
  ]

  responses, rejected_records = calculate_responses(records)

  assert len(responses) == 1
  assert responses[0]["trial_id"] == "T002"

  assert len(rejected_records) == 1
  report = rejected_records[0]

  assert report["invalid_fields"] == ["current"]
  assert report["record"]["trial_id"] == "T001"

def test_out_of_range_values_are_reported():
  records = [
    {"trial_id": "T006", "frequency_hz": 0, "current": -0.019, "voltage": 5.0}
  ]

  responses, rejected_records = calculate_responses(records)

  assert responses == []
  assert len(rejected_records) == 1

  report = rejected_records[0]

  assert report["invalid_fields"] == ["frequency_hz", "current"]

def test_nonfinite_current_is_rejected():
  records = [
    {"trial_id": "T001", "frequency_hz": 100.0, "current": float("nan"), "voltage": 5.0}
  ]

  responses, rejected_records = calculate_responses(records)

  assert responses == []
  assert len(rejected_records) == 1

  report = rejected_records[0]

  assert report["invalid_fields"] == ["current"]
  assert report["reason"] == "nonfinite numeric values"

def test_blank_trial_id_is_rejected():
  records = [
    {"trial_id": "   ", "frequency_hz": 100.0, "current": 0.019, "voltage": 5.0}
  ]

  responses, rejected_records = calculate_responses(records)

  assert responses == []
  assert len(rejected_records) == 1

  report = rejected_records[0]
  assert report["invalid_fields"] == ["trial_id"]
  assert report["reason"] == "trial_id must be a nonblank string"

def test_duplicate_frequencies():
  responses = [
    {"frequency_hz": 300.0},
    {"frequency_hz": 400.0},
    {"frequency_hz": 400.0},
    {"frequency_hz": 400.0},
    {"frequency_hz": 500.0}
  ]

  duplicates = find_duplicate_frequencies(responses)

  assert len(duplicates) == 1
  assert duplicates == [400]

def test_unique_frequencies():
  responses = [
    {"frequency_hz": 300.0},
    {"frequency_hz": 400.0},
    {"frequency_hz": 500.0}
  ]

  duplicates = find_duplicate_frequencies(responses)

  assert duplicates == []

def test_response_overflow_is_rejected():
  records = [
  {
    "trial_id": "T001",
    "frequency_hz": 100.0,
    "current": 1e308,
    "voltage": 1e-308
  }
  ]

  responses, rejected_records = calculate_responses(records)

  assert responses == []
  assert len(rejected_records) == 1

  report = rejected_records[0]
  assert report["reason"] == "calculated response is nonfinite"

def test_load_invalid_json(tmp_path):
  file_path = tmp_path / "broken.json"
  file_path.write_text('{"trial_id":', encoding="utf-8")

  records = load_sweep(file_path)

  assert records == []

def test_load_valid_json(tmp_path):
  file_path = tmp_path / "valid.json"
  file_path.write_text(
    '[{"trial_id": "T001", "frequency_hz": 100.0, "current": 0.01, "voltage": 5.0}]',
    encoding="utf-8"
  )

  records = load_sweep(file_path)

  assert len(records) == 1
  assert records[0]["trial_id"] == "T001"
  assert records[0]["current"] == 0.01