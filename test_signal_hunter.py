from signal_hunter import find_peak, inspect_peak, calculate_responses

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

  responses = calculate_responses(records)

  assert len(responses) == 1
  assert responses[0]["trial_id"] == "T002"

def test_all_zero_voltages():
  records = [
    {"trial_id": "T001", "frequency_hz": 100.0, "current": 0.01, "voltage": 0},
    {"trial_id": "T002", "frequency_hz": 200.0, "current": 0.02, "voltage": 0}
  ]

  responses = calculate_responses(records)

  assert responses == []
  assert len(responses) == 0

def test_invalid_numeric_values_are_skipped():
  records = [
    {"trial_id": "T001", "frequency_hz": 100.0, "current": "hello", "voltage": 5.0},
    {"trial_id": "T002", "frequency_hz": 200.0, "current": True, "voltage": 5.0},
    {"trial_id": "T003", "frequency_hz": 300.0, "current": 0.019, "voltage": 5.0}
  ]

  responses = calculate_responses(records)

  assert len(responses) == 1
  assert responses[0]["trial_id"] == "T003"

def test_missing_current_is_skipped():
  records = [
    {"trial_id": "T001", "frequency_hz": 100.0, "voltage": 5.0},
    {"trial_id": "T002", "frequency_hz": 200.0, "current": 0.02, "voltage": 5.0}
  ]

  responses = calculate_responses(records)

  assert len(responses) == 1
  assert responses[0]["trial_id"] == "T002"