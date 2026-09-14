# Signal Hunter

A Python tool for examining frequency-sweep measurements. It validates input records, calculates current-to-voltage response, identifies the strongest measured response, and plots the results alongside information about skipped measurements.

Built as a standalone companion to my Experimental Data Quality Inspector project.

## What it does

- Loads measurements from a JSON file.
- Checks required fields, numeric types, finite values, and allowed ranges.
- Preserves rejected measurements with field names and rejection reasons.
- Calculates response as current divided by voltage.
- Sorts usable measurements by frequency.
- Finds the strongest measured response.
- Checks whether it lies at a sweep boundary or exceeds both immediate usable neighbors.
- Flags repeated frequencies and withholds neighbor assessment when they occur.
- Plots measurements with trial labels, a peak marker, and skipped-measurement counts.
- Marks rejected measurements at their frequencies when those frequencies are usable.

## Example data

`frequency_sweep.json` contains seven handcrafted practice measurements. These are not real experimental measurements or results from a physical circuit simulation.

The example uses these conventions:

| Field | Meaning | Requirement |
|---|---|---|
| `trial_id` | Measurement identifier | Nonblank string |
| `frequency_hz` | Applied frequency in hertz | Positive, finite number |
| `voltage` | Applied RMS voltage in volts | Positive, finite number |
| `current` | RMS current in amps | Nonnegative, finite number |
| `temperature` | Temperature in kelvin | Optional; not analyzed |

Boolean values are not accepted as numeric measurements. Calculated responses must also be finite.

The JSON file must contain a list of measurement dictionaries:

```json
[
  {
    "trial_id": "T001",
    "frequency_hz": 100.0,
    "voltage": 5.0,
    "current": 0.010,
    "temperature": 295.0
  }
]
```

## Setup and use

Requires Python 3 and the Matplotlib package. Tests use pytest.

Install the packages into your chosen Python environment:

```sh
python3 -m pip install -r requirements.txt
```

From the project directory, run:

```sh
python3 signal_hunter.py
```

The program reads `frequency_sweep.json`, prints its findings, and opens a plot window. Close the plot window to finish the run.

With the original practice dataset, the strongest response is:

```text
T004 | 400.0 Hz | 0.0100 A/V
```

To use a different input file, change `file_name` in `main()`.

## Tests

Run the regression tests with:

```sh
python3 -m pytest test_signal_hunter.py
```

The suite covers peak selection, boundary and tied peaks, repeated frequencies, rejected measurements, calculated-response overflow, and valid and malformed JSON loading.

## Project structure

- `signal_hunter.py` — loading, validation, analysis, reporting, and plotting.
- `frequency_sweep.json` — handcrafted example measurements.
- `test_signal_hunter.py` — regression tests.
- `requirements.txt` — dependencies for running the program and tests.

## Interpretation and limitations

The selected peak is the strongest response among the usable sampled measurements. It is not proof of resonance and does not estimate what happens between sampled frequencies.

Neighbor comparisons use the remaining usable measurements. Rejected records can leave gaps, and the program does not yet assess how those gaps affect confidence near the peak.

Plot lines connect usable points as a visual guide; they do not represent measurements between those points. Dashed markers show rejected measurement frequencies, not rejected response values. Rejections with unusable frequencies are counted but cannot be positioned on the plot.

Repeated frequencies remain visible, but neighbor assessment is withheld. Equal maximum responses are resolved by keeping the first encountered after sorting.

The tool does not distinguish a narrow physical peak from an isolated measurement spike, quantify uncertainty, or combine repeated measurements.

## Future work

- Integrate with Experimental Data Quality Inspector.
- Evaluate gaps near a candidate peak.
- Add physically simulated and real experimental sweep datasets.