# Smart Fitness Session Analyzer 
import statistics
from data_generator import available_scenarios, generate_fitness_data



class Metric:
    "Metric class represents a single observation within a session."
    
    MIN_SIGNAL_QUALITY = 0.60

    def __init__(self, timestamp: int, signal_quality: float):
        self.timestamp = timestamp
        # Implemented Encapsulation: Protected attribute
        self._signal_quality = signal_quality

    @property
    def signal_quality(self) -> float:
        """Getter property for signal quality."""
        return self._signal_quality

    def is_signal_valid(self) -> bool:
        """Validates basic signal quality parameter."""
        if self._signal_quality is None or not isinstance(self._signal_quality, (int, float)):
            return False
        return 0.0 <= self._signal_quality <= 1.0 and self._signal_quality >= self.MIN_SIGNAL_QUALITY

    def is_valid(self) -> bool:
        """Polymorphic validation method to be overridden by child classes."""
        return self.is_signal_valid()

    def get_summary(self) -> str:
        """Base string representation of the observation window."""
        return f"Timestamp: {self.timestamp} | Signal Quality: {self._signal_quality}"


class FitnessObservation(Metric):
    """This derived class representing domain-specific wearable fitness sensor metrics."""

    # as specified in zip folder
    HR_RANGE = (35, 205)
    TEMP_RANGE = (25.0, 42.0)
    ACTIVITY_RANGE = (0.0, 1.0)

    def __init__(self, timestamp: int, heart_rate, skin_response, temperature, activity_level, signal_quality):

        super().__init__(timestamp, signal_quality)
        self.heart_rate = heart_rate
        self.skin_response = skin_response
        self.temperature = temperature
        self.activity_level = activity_level

    def is_valid(self) -> bool:
        """
        Implemented Method Overriding: Extends Metric.is_valid() by adding domain-specific
        bounds checking and null validation.
        """
        if not super().is_valid():
            return False

        # Rejecting missing values 
        if None in (self.heart_rate, self.skin_response, self.temperature, self.activity_level):
            return False

        # here we are reject impossible range values
        if not (self.HR_RANGE[0] <= self.heart_rate <= self.HR_RANGE[1]):
            return False
        if not (self.TEMP_RANGE[0] <= self.temperature <= self.TEMP_RANGE[1]):
            return False
        if not (self.ACTIVITY_RANGE[0] <= self.activity_level <= self.ACTIVITY_RANGE[1]):
            return False
        if self.skin_response < 0:
            return False

        return True

    def get_summary(self) -> str:
        """Method Overriding: Extends Observation.get_summary with detailed fitness metrics."""
        base_summary = super().get_summary()
        if not self.is_valid():
            return f"{base_summary} | Status: INVALID"
        return f"{base_summary} | HR: {self.heart_rate} bpm | Activity: {self.activity_level} | Temp: {self.temperature}°C"


class Participant:
    """Represents a gym participant and encapsulates personal baseline measurements."""

    def __init__(self, participant_id: str, baseline_hr: float, baseline_skin: float, baseline_temp: float):
        self.participant_id = participant_id
        # Encapsulation: Private attributes
        self.__baseline_hr = baseline_hr
        self.__baseline_skin = baseline_skin
        self.__baseline_temp = baseline_temp

    @property
    def baseline_hr(self) -> float:
        """Property getter for baseline heart rate."""
        return self.__baseline_hr

    @property
    def baseline_skin(self) -> float:
        """Property getter for baseline skin response."""
        return self.__baseline_skin

    @property
    def baseline_temp(self) -> float:
        """Property getter for baseline skin temperature."""
        return self.__baseline_temp

    @classmethod
    def from_dict(cls, profile_dict: dict):
        """Class Method: Factory constructor to instantiate Participant from raw generator dictionary."""
        return cls(
            participant_id=profile_dict.get("participant_id", "Unknown"),
            baseline_hr=profile_dict.get("baseline_heart_rate", 70.0),
            baseline_skin=profile_dict.get("baseline_skin_response", 1.5),
            baseline_temp=profile_dict.get("baseline_temperature", 32.0),
        )


class FitnessSession:
    """
    Represents a training session containing participant info and observation windows.
    Demonstrates Composition: Composes Participant and FitnessObservation objects.
    """

    def __init__(self, participant: Participant, observations: list = None):
        self.participant = participant  # Composition
        self.observations = observations if observations is not None else []  # Composition

    def add_observation(self, obs: FitnessObservation):
        """Add an observation instance to the session list."""
        self.observations.append(obs)

    def get_valid_observations(self) -> list:
        """Filter and return only valid observation objects."""
        return [obs for obs in self.observations if obs.is_valid()]

    def get_invalid_observations(self) -> list:
        """Filter and return only invalid/flagged observation objects."""
        return [obs for obs in self.observations if not obs.is_valid()]


class SessionAnalyzer:
    """Performs statistical analysis, recovery evaluation, and classification on a session."""

    def __init__(self, session: FitnessSession):
        self.session = session

    @staticmethod
    def is_insufficient_data(valid_count: int, total_count: int) -> bool:
        """Static Method: Utility to check if usable data falls below required threshold."""
        return valid_count < 4 or (total_count > 0 and (valid_count / total_count) < 0.50)

    def analyze(self) -> dict:
        """Processes the session and returns a structured analysis result dictionary."""
        p = self.session.participant
        all_obs = self.session.observations
        valid_obs = self.session.get_valid_observations()

        total_count = len(all_obs)
        valid_count = len(valid_obs)
        rejected_count = total_count - valid_count
        usable_pct = round((valid_count / total_count * 100), 1) if total_count > 0 else 0.0

        data_quality = {
            "total_observations": total_count,
            "usable_observations": valid_count,
            "rejected_observations": rejected_count,
            "usable_percentage": usable_pct,
        }

        # Check for insufficient data scenario
        if self.is_insufficient_data(valid_count, total_count):
            return {
                "participant_id": p.participant_id,
                "classification": "insufficient data",
                "explanation": f"Only {valid_count} of {total_count} observations were valid ({usable_pct}%). Minimum requirement: 4 valid windows and ≥50% signal quality.",
                "data_quality": data_quality,
                "summaries": {},
                "baseline_comparison": {},
            }

        # Extract numerical metrics from valid observations
        hrs = [o.heart_rate for o in valid_obs]
        skins = [o.skin_response for o in valid_obs]
        temps = [o.temperature for o in valid_obs]
        activities = [o.activity_level for o in valid_obs]

        summaries = {
            "heart_rate": calculate_summary_statistics(hrs),
            "skin_response": calculate_summary_statistics(skins),
            "temperature": calculate_summary_statistics(temps),
            "activity_level": calculate_summary_statistics(activities),
        }

        avg_hr = summaries["heart_rate"]["mean"]
        avg_act = summaries["activity_level"]["mean"]
        avg_temp = summaries["temperature"]["mean"]
        avg_skin = summaries["skin_response"]["mean"]

        hr_delta = round(avg_hr - p.baseline_hr, 2)
        hr_pct = round((hr_delta / p.baseline_hr) * 100, 1)

        baseline_comp = {
            "baseline_hr": p.baseline_hr,
            "session_avg_hr": avg_hr,
            "hr_delta": hr_delta,
            "hr_percent_change": hr_pct,
            "baseline_temp": p.baseline_temp,
            "session_avg_temp": avg_temp,
            "temp_delta": round(avg_temp - p.baseline_temp, 2),
            "baseline_skin": p.baseline_skin,
            "session_avg_skin": avg_skin,
            "skin_delta": round(avg_skin - p.baseline_skin, 2),
        }

        # Evaluate Recovery Trend
        is_recovering, rec_reason = detect_recovery_pattern(valid_obs, p.baseline_hr)

        # Classification rules
        if is_recovering:
            classification = "recovering"
            explanation = f"Recovery trend confirmed: {rec_reason}"
        elif avg_act >= 0.65 or avg_hr >= p.baseline_hr + 45:
            classification = "high activity"
            explanation = f"Average activity ({avg_act:.2f}) and HR elevation (+{hr_delta:.1f} bpm) reflect intense physical exertion."
        elif avg_act >= 0.30 or avg_hr >= p.baseline_hr + 15:
            classification = "moderate activity"
            explanation = f"Average activity ({avg_act:.2f}) and HR elevation (+{hr_delta:.1f} bpm) indicate moderate physical effort."
        else:
            classification = "resting"
            explanation = f"Average activity ({avg_act:.2f}) and HR ({avg_hr:.1f} bpm) remain close to personal baseline levels."

        return {
            "participant_id": p.participant_id,
            "classification": classification,
            "explanation": explanation,
            "data_quality": data_quality,
            "summaries": summaries,
            "baseline_comparison": baseline_comp,
        }



# STANDALONE FUNCTIONS

def validate_observation_data(obs_dict: dict) -> bool:
    """Standalone Function 1: Validates raw observation dictionary fields and ranges."""
    if not isinstance(obs_dict, dict):
        return False
    required_keys = {"timestamp", "heart_rate", "skin_response", "temperature", "activity_level", "signal_quality"}
    if not required_keys.issubset(obs_dict.keys()):
        return False

    obs = FitnessObservation(
        timestamp=obs_dict.get("timestamp"),
        heart_rate=obs_dict.get("heart_rate"),
        skin_response=obs_dict.get("skin_response"),
        temperature=obs_dict.get("temperature"),
        activity_level=obs_dict.get("activity_level"),
        signal_quality=obs_dict.get("signal_quality"),
    )
    return obs.is_valid()


def calculate_summary_statistics(data_list: list) -> dict:
    """Standalone Function 2: Computes average, min, max, and std deviation for numeric sequences."""
    if not data_list:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "std_dev": 0.0}

    mean_val = statistics.mean(data_list)
    std_val = statistics.stdev(data_list) if len(data_list) > 1 else 0.0
    return {
        "mean": round(mean_val, 2),
        "min": round(min(data_list), 2),
        "max": round(max(data_list), 2),
        "std_dev": round(std_val, 2),
    }


def detect_recovery_pattern(valid_obs: list, baseline_hr: float) -> tuple:
    """Standalone Function 3: Analyzes trend trajectories of HR and activity across session halves."""
    if len(valid_obs) < 4:
        return False, "Insufficient data windows to evaluate recovery pattern."

    mid = len(valid_obs) // 2
    first_half = valid_obs[:mid]
    second_half = valid_obs[mid:]

    avg_hr_early = statistics.mean([o.heart_rate for o in first_half])
    avg_hr_late = statistics.mean([o.heart_rate for o in second_half])

    avg_act_early = statistics.mean([o.activity_level for o in first_half])
    avg_act_late = statistics.mean([o.activity_level for o in second_half])

    hr_decline_ratio = (avg_hr_early - avg_hr_late) / avg_hr_early if avg_hr_early > 0 else 0
    act_decline = avg_act_early - avg_act_late

    # Active first half followed by clear decline near end
    if avg_hr_early > baseline_hr + 15 and hr_decline_ratio >= 0.15 and act_decline >= 0.15:
        reason = (f"Heart rate dropped {hr_decline_ratio * 100:.1f}% ({avg_hr_early:.1f} → {avg_hr_late:.1f} bpm) "
                  f"and activity declined by {act_decline:.2f}.")
        return True, reason

    return False, f"No significant recovery trajectory detected (HR drop: {hr_decline_ratio * 100:.1f}%, Activity drop: {act_decline:.2f})."


def format_console_report(report_dict: dict) -> str:
    """Standalone Function 4: Renders a structured dictionary into a clean console report."""
    lines = []
    lines.append("=" * 68)
    lines.append(f"          SMART FITNESS SESSION REPORT - PARTICIPANT: {report_dict['participant_id']}")
    lines.append("=" * 68)

    lines.append(f"CLASSIFICATION      : {report_dict['classification'].upper()}")
    lines.append(f"EXPLANATION         : {report_dict['explanation']}")
    lines.append("-" * 68)

    q = report_dict["data_quality"]
    lines.append("DATA QUALITY METRICS:")
    lines.append(f"  • Total Windows Received : {q['total_observations']}")
    lines.append(f"  • Usable Windows Accepted: {q['usable_observations']}")
    lines.append(f"  • Invalid Windows Flagged: {q['rejected_observations']}")
    lines.append(f"  • Data Usability Rate    : {q['usable_percentage']}%")
    lines.append("-" * 68)

    if report_dict["classification"] != "insufficient data":
        lines.append("FEATURE SUMMARY STATISTICS (Usable Data Only):")
        for feature, stats in report_dict["summaries"].items():
            name = feature.replace("_", " ").title()
            lines.append(f"  • {name:<18}: Mean={stats['mean']:<6} Min={stats['min']:<6} Max={stats['max']:<6} Std={stats['std_dev']}")

        lines.append("-" * 68)
        comp = report_dict["baseline_comparison"]
        lines.append("BASELINE REFERENCE COMPARISON:")
        lines.append(f"  • Heart Rate Baseline : {comp['baseline_hr']} bpm -> Avg: {comp['session_avg_hr']} bpm (Diff: {comp['hr_delta']:+0.2f} bpm, {comp['hr_percent_change']:+0.1f}%)")
        lines.append(f"  • Temperature Baseline: {comp['baseline_temp']}°C -> Avg: {comp['session_avg_temp']}°C (Diff: {comp['temp_delta']:+0.2f}°C)")
        lines.append(f"  • Skin Resp Baseline  : {comp['baseline_skin']} -> Avg: {comp['session_avg_skin']} (Diff: {comp['skin_delta']:+0.2f})")

    lines.append("=" * 68)
    return "\n".join(lines)



# MAIN FUNCTION

def main():
    print("Executing Smart Fitness Session Analyzer For All Scenarios.......\n")

    scenarios = available_scenarios()
    for index, scenario_name in enumerate(scenarios, start=1):
        print(f"\n>>> Running Scenario {index}/{len(scenarios)}: '{scenario_name}'")

        # Call instructor-provided data generator
        profile, observations_raw = generate_fitness_data(
            participant_id=f"P00{index}",
            scenario=scenario_name,
            seed=42,
            number_of_windows=12,
        )

        # Building Domain Objects
        participant = Participant.from_dict(profile)
        session = FitnessSession(participant)

        for obs_dict in observations_raw:
            obs = FitnessObservation(
                timestamp=obs_dict.get("timestamp"),
                heart_rate=obs_dict.get("heart_rate"),
                skin_response=obs_dict.get("skin_response"),
                temperature=obs_dict.get("temperature"),
                activity_level=obs_dict.get("activity_level"),
                signal_quality=obs_dict.get("signal_quality"),
            )
            session.add_observation(obs)

        # Analysis and Presentation
        analyzer = SessionAnalyzer(session)
        analysis_result = analyzer.analyze()
        report_text = format_console_report(analysis_result)
        print(report_text)


if __name__ == "__main__":
    main()