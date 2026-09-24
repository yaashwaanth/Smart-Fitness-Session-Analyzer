# Smart Fitness Session Analyzer

**Course:** Problem Solving with Scripting 
**Option:** Option A – Smart Fitness Session Analyzer  
**Student Name:** G Yashwanth Sharma  
**Student ID:** 416277

---

## 1. Background
A fitness centre receives simulated measurements from wearable devices used during training sessions. It needs a Python
program that organizes participants and exercise sessions, validates measurements, compares measurements with personal
reference values, classifies session intensity and describes recovery after activity.

---

## 2. Object-Oriented Design & Responsibilities

The program consists of 5 domain classes and 4 standalone functions:

### Class Architecture & Responsibilities
1. **`Metric` (Base Class):**
   * Encapsulates timestamp and raw signal quality (`_signal_quality`).
   * Provides base validation (`is_signal_valid()`).
2. **`FitnessObservation` (Subclass of `Metric`):**
   * Extends base Metric with domain metrics (`heart_rate`, `skin_response`, `temperature`, `activity_level`).
   * Overrides `is_valid()` to check domain constraints ($35 \le HR \le 205$, $25 \le Temp \le 42^\circ C$, $0 \le Activity \le 1.0$).
3. **`Participant`:**
   * Encapsulates participant baseline metrics as private attributes (`__baseline_hr`, `__baseline_skin`, `__baseline_temp`).
   * Uses `@classmethod` (`from_dict`) as a factory constructor.
4. **`FitnessSession` (Composition Container):**
   * Composes a `Participant` instance and a `list` of `FitnessObservation` objects.
   * Manages filtering of valid vs. invalid observations.
5. **`SessionAnalyzer`:**
   * Performs statistical aggregation, baseline comparisons, recovery trajectory evaluation, and classification.
   * Features `@staticmethod` (`is_insufficient_data`).

### OOP Principles Applied
* **Composition:** `FitnessSession` contains a `Participant` object and a list of `FitnessObservation` objects.
* **Encapsulation:** Baseline parameters in `Participant` use double underscores (`__baseline_hr`) and getter properties.
* **Inheritance & Method Overriding:** `FitnessObservation` inherits from `Metric` and overrides `is_valid()` and `get_summary()`.
* **Class Methods & Static Methods:** `Participant.from_dict()` (`@classmethod`) and `SessionAnalyzer.is_insufficient_data()` (`@staticmethod`).

---

## 3. Standalone Functions
1. `validate_observation_data(obs_dict)`: Validates raw observation payload dictionaries.
2. `calculate_summary_statistics(data_list)`: Calculates mean, min, max, and standard deviation.
3. `detect_recovery_pattern(valid_obs, baseline_hr)`: Evaluates declining trajectories in heart rate and activity level across session halves.
4. `format_console_report(report_dict)`: Formats structured result dictionaries into formatted text reports.

---

## 4. Classification Rules & Assumptions
* **Insufficient Data:** Usable windows $< 4$ or usability rate $< 50\%$.
* **Recovering:** High activity/HR in the first half followed by a $\ge 15\%$ decline in HR and activity near session end.
* **High Activity:** Mean activity $\ge 0.65$ or HR elevated by $\ge 45\text{ bpm}$ over baseline.
* **Moderate Activity:** Mean activity $\ge 0.30$ or HR elevated by $\ge 15\text{ bpm}$ over baseline.
* **Resting:** Activity and HR remain near resting baseline levels.

---

## 5. Execution Instructions

### Running the Program
```bash
git clone [https://github.com/yaashwaanth/Smart-Fitness-Session-Analyzer.git]
**Actual way to run the code:** python3 main.py

**Alternative way to run the code,if above command does not run:** python main.py
```

---
## 6. Known Limitations
* The program detects recovery by dividing the session directly in half. In real life, workouts can have different stages, so splitting the session in half might miss shorter recovery periods.

* If a single sensor reading in a time window is missing or wrong, the entire window is dropped. A real system might try to fix the missing value instead of throwing away all sensor readings for that timestamp.

