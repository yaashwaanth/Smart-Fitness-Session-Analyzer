# Smart Fitness Session Analyzer

A Python-based command-line tool designed to process, validate, and analyze wearable sensor observations during workout sessions. The tool filters invalid observations, calculates summary statistics, evaluates recovery trends, and generates structured analytical reports.

---

## Requirements

Uses standard library modules: `pathlib`, `csv`, `argparse`, `statistics`, `re`, `sys`

No external third-party dependencies are required.

---

## File Structure

```text
.
├── main.py             # CLI entry point, file parsing, and report generation
├── analyzer.py         # SessionAnalyzer, statistical calculation, and recovery detection logic
├── core_modules.py     # Metric, FitnessObservation, Participant, and FitnessSession classes
├── exceptions.py       # Custom exception classes (InvalidIdentifierError, InvalidRecordError)
└── README.md           # Instructions and usage documentation
```

---
## Command To run the program


`python3 main.py --profiles data/participants.csv --sessions data/fitness_sessions.csv data/fitness_sessions_invalid.csv --output output`


