import json
import matplotlib.pyplot as plt
import math

def load_sweep(file_name):
  try:
    with open(file_name, "r") as file:
      sweep_records = json.load(file)

  except FileNotFoundError:
    print(f"{file_name} could not be located.")
    sweep_records = []

  except json.JSONDecodeError:
    print(f"{file_name} contains invalid JSON syntax.")
    sweep_records = []

  except UnicodeDecodeError:
    print(f"{file_name} could not be decoded as text.")
    sweep_records = []

  except OSError as error:
    print(f"{file_name} could not be read: {error}")
    sweep_records = []

  if not isinstance(sweep_records, list):
    print("Expected a list of measurements.")
    return []

  return sweep_records

def calculate_responses(records):
  responses = []
  rejected_records = []
  required_fields = ["trial_id", "frequency_hz", "current", "voltage"]
  numeric_fields = ["frequency_hz", "current", "voltage"]

  for record in records:
    if not isinstance(record, dict):
      rejection_report = {
        "record": record,
        "invalid_fields": [],
        "reason": "measurement is not a dictionary"
      }

      rejected_records.append(rejection_report)
      continue

    missing_fields = []

    for field in required_fields:
      if field not in record:
        missing_fields.append(field)

    if missing_fields:
      rejection_report = {
        "record": record,
        "invalid_fields": missing_fields,
        "reason": "missing required fields"
      }

      trial_id = record.get("trial_id", "Unknown trial")

      rejected_records.append(rejection_report)
      continue

    trial_id = record["trial_id"]

    if not isinstance(trial_id, str) or not trial_id.strip():
      rejection_report = {
        "record": record,
        "invalid_fields": ["trial_id"],
        "reason": "trial_id must be a nonblank string"
      }

      rejected_records.append(rejection_report)
      continue

    invalid_fields = []

    for field in numeric_fields:
      value = record[field]

      if not isinstance(value, (int, float)) or isinstance(value, bool):
        invalid_fields.append(field)

    if invalid_fields:
      rejection_report = {
        "record": record,
        "invalid_fields": invalid_fields,
        "reason": "invalid numeric type"
      }

      rejected_records.append(rejection_report)
      continue

    invalid_fields = []

    for field in numeric_fields:
      if not math.isfinite(record[field]):
        invalid_fields.append(field)

    if invalid_fields:
      rejection_report = {
        "record": record,
        "invalid_fields": invalid_fields,
        "reason": "nonfinite numeric values"
      }

      rejected_records.append(rejection_report)
      continue

    invalid_fields = []

    if record["frequency_hz"] <= 0:
      invalid_fields.append("frequency_hz")

    if record["voltage"] < 0:
      invalid_fields.append("voltage")

    if record["current"] < 0:
      invalid_fields.append("current")

    if invalid_fields:
      rejection_report = {
        "record": record,
        "invalid_fields": invalid_fields,
        "reason": "values outside allowed physical range"
      }

      rejected_records.append(rejection_report)
      continue

    if record["voltage"] == 0:
      rejection_report = {
        "record": record,
        "invalid_fields": ["voltage"],
        "reason": "zero voltage"
      }

      rejected_records.append(rejection_report)
      continue

    response = record["current"] / record["voltage"]

    if not math.isfinite(response):
      rejection_report = {
        "record": record,
        "invalid_fields": ["current", "voltage"],
        "reason": "calculated response is nonfinite"
      }

      rejected_records.append(rejection_report)
      continue

    result = {
      "trial_id": record["trial_id"],
      "frequency_hz": record["frequency_hz"],
      "response": response
    }

    responses.append(result)

  return responses, rejected_records

def find_peak(responses):
  peak = responses[0]

  for result in responses[1:]:
    if result["response"] > peak["response"]:
      peak = result

  return peak

def get_frequency(result):
  return result["frequency_hz"]


def inspect_peak(responses, peak):
  peak_index = responses.index(peak)

  if peak_index == 0 or peak_index == len(responses) - 1:
    return "Peak is at the sweep boundary; cannot inspect both sides."
  else:
    left_neighbor = responses[peak_index - 1]
    right_neighbor = responses[peak_index + 1]

  if peak["response"] > left_neighbor["response"] and peak["response"] > right_neighbor["response"]:
    finding = "Peak response is higher than both immediate neighbors."
    return finding
  else:
    return "the peak is not strictly higher than both immediate neighbors."

def find_duplicate_frequencies(responses):
  duplicates = []

  if not responses:
    return duplicates

  previous_frequency = responses[0]["frequency_hz"]

  for result in responses[1:]:
    frequency = result["frequency_hz"]

    if previous_frequency == frequency and frequency not in duplicates:
      duplicates.append(frequency)

    previous_frequency = frequency

  return duplicates

def plot_responses(responses, peak, rejected_records):
  frequencies = []
  response_values = []

  for result in responses:
    frequency = result["frequency_hz"]
    response = result["response"]
    frequencies.append(frequency)
    response_values.append(response)

  plt.plot(frequencies, response_values, marker="o")

  for result in responses:
    plt.annotate(
      result["trial_id"],
      (result["frequency_hz"], result["response"]),
      xytext=(0, 8),
      textcoords="offset points",
      ha="center"
    )

  plt.xlabel("Frequency (Hz)")
  plt.ylabel("Respomses (A/V)")
  plt.title(
    f"Signal Hunter: Frequency Sweep\n"
    f"{len(responses)} usable measurements | {len(rejected_records)} skipped"
  )

  plt.scatter(
    peak["frequency_hz"],
    peak["response"],
    color="red",
    s=100,
    label="Strongest measured response"
  )

  rejection_label_added = False

  for report in rejected_records:
    record = report["record"]

    # Check that record is a dictionary before accessing its fields.
    if not isinstance(record, dict):
      continue

    frequency = record.get("frequency_hz")

    if not isinstance(frequency, (int, float)) or isinstance(frequency, bool):
      continue

    if not math.isfinite(frequency) or frequency <= 0:
      continue

    if not rejection_label_added:
      plt.axvline(
        x=frequency,
        color="gray",
        linestyle="--",
        label="Skipped measurement"
      )
      rejection_label_added = True
    else:
      plt.axvline(x=frequency, color="gray", linestyle="--")

  plt.legend()


  plt.show()

def show_rejections(rejected_records):
  for report in rejected_records:
    record = report["record"]
    trial_id = "Unknown trial"

    if isinstance(record, dict):
      candidate = record.get("trial_id")

      if isinstance(candidate, str) and candidate.strip():
        trial_id = candidate

    print(
      f"Skipped {trial_id}: {report['reason']} "
      f"| fields: {report['invalid_fields']}"
    )

def main():
  project_name = "Signal Hunter"
  file_name = "frequency_sweep.json"

  sweep_records = load_sweep(file_name)

  if not sweep_records:
    print("No measurements to analyze; dataset empty.")

    return

  responses, rejected_records = calculate_responses(sweep_records)

  if not responses:
    show_rejections(rejected_records)
    print("No usable responses to analyze.")
    return

  responses = sorted(responses, key=get_frequency)
  duplicate_frequencies = find_duplicate_frequencies(responses)

  for result in responses:
    print(f"{result['trial_id']} | {result['frequency_hz']} Hz | {result['response']:.4f} A/V")

  peak = find_peak(responses)
  if duplicate_frequencies:
    finding = (
      f"Repeated frequencies: {duplicate_frequencies} Hz; "
      "neighbor assessment cannot be made."
    )
  else:
    finding = inspect_peak(responses, peak)
  print(finding)

  if rejected_records:
    print(f"{len(rejected_records)} measurement(s) were skipped; peak assessment uses only usable measurements.")

  print(f"Strongest measured response: {peak['trial_id']} | {peak['frequency_hz']} Hz | {peak['response']:.4f} A/V")

  show_rejections(rejected_records)
  plot_responses(responses, peak, rejected_records)

if __name__ == "__main__":
  main()