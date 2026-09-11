import json
import matplotlib.pyplot as plt

def load_sweep(file_name):
  with open("frequency_sweep.json", "r") as file:
    sweep_records = json.load(file)

  return sweep_records

def calculate_responses(records):
  responses = []

  for record in records:
      response = record["current"] / record["voltage"]

      result = {
          "trial_id": record["trial_id"],
          "frequency_hz": record["frequency_hz"],
          "response": response
      }

      responses.append(result)

  return responses

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

def plot_responses(responses, peak):
  frequencies = []
  response_values = []

  for result in responses:
    frequency = result["frequency_hz"]
    response = result["response"]
    frequencies.append(frequency)
    response_values.append(response)

  plt.plot(frequencies, response_values, marker="o")

  plt.xlabel("Frequency (Hz)")
  plt.ylabel("Respomses (A/V)")
  plt.title("Signal Hunter: Frequency Sweep")

  plt.scatter(
    peak["frequency_hz"],
    peak["response"],
    color="red",
    s=100,
    label="Strongest measured response"
  )

  plt.legend()


  plt.show()

def main():
  project_name = "Signal Hunter"
  file_name = "frequency_sweep.json"

  sweep_records = load_sweep(file_name)

  responses = calculate_responses(sweep_records)
  responses = sorted(responses, key=get_frequency)

  for result in responses:
    print(f"{result['trial_id']} | {result['frequency_hz']} Hz | {result['response']:.4f} A/V")

  peak = find_peak(responses)
  finding = inspect_peak(responses, peak)
  print(finding)

  print(f"Strongest measured response: {peak['trial_id']} | {peak['frequency_hz']} Hz | {peak['response']:.4f} A/V")

  plot_responses(responses, peak)

if __name__ == "__main__":
  main()