import statistics

from core_modules import FitnessSession

class SessionAnalyzer:
    """Performs statistical analysis, recovery evaluation, and classification on a session."""

    def __init__(self, session: FitnessSession):
        self.session = session

    @staticmethod
    def is_insufficient_data(valid_count: int, total_count: int) -> bool:
        """Static Method: Utility to check if usable data falls below required threshold."""
        return valid_count < 4 or (total_count > 0 and (valid_count / total_count) < 0.50)

    def analyze(self, total_rows_attempted: int = None) -> dict:
        """Processes the session and returns a structured analysis result dictionary."""
        p = self.session.participant
        all_obs = self.session.observations
        valid_obs = self.session.get_valid_observations()

        total_count = total_rows_attempted if total_rows_attempted is not None else len(all_obs)
        valid_count = len(valid_obs)
        rejected_count = total_count - valid_count
        usable_pct = round((valid_count / total_count * 100), 1) if total_count > 0 else 0.0

        data_quality = {
            "total_observations": total_count,
            "usable_observations": valid_count,
            "rejected_observations": rejected_count,
            "usable_percentage": usable_pct,
        }






        # Checking for insufficient data scenario
        if self.is_insufficient_data(valid_count, total_count):
            return {
                "session_id": self.session.session_id,  
                "participant_id": p.participant_id,
                "classification": "insufficient data",
                "explanation": f"Only {valid_count} of {total_count} observations were valid ({usable_pct}%). Minimum requirement: 4 valid windows and ≥50% signal quality.",
                "data_quality": data_quality,
                "summaries": {},
                "baseline_comparison": {},
            }

        # Extracting numerical metrics from valid observations
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

        # Evaluating Recovery Trend
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
            "session_id": self.session.session_id, 
            "participant_id": p.participant_id,
            "classification": classification,
            "explanation": explanation,
            "data_quality": data_quality,
            "summaries": summaries,
            "baseline_comparison": baseline_comp,
        }

# STANDALONE FUNCTIONS

# def validate_observation_data(obs_dict: dict) -> bool:
#     """Standalone Function 1: Validates raw observation dictionary fields and ranges."""
#     if not isinstance(obs_dict, dict):
#         return False
#     required_keys = {"timestamp", "heart_rate", "skin_response", "temperature", "activity_level", "signal_quality"}
#     if not required_keys.issubset(obs_dict.keys()):
#         return False

#     obs = FitnessObservation(
#         timestamp=obs_dict.get("timestamp"),
#         heart_rate=obs_dict.get("heart_rate"),
#         skin_response=obs_dict.get("skin_response"),
#         temperature=obs_dict.get("temperature"),
#         activity_level=obs_dict.get("activity_level"),
#         signal_quality=obs_dict.get("signal_quality"),
#     )
#     return obs.is_valid()


# def format_console_report(report_dict: dict) -> str:
#     """Standalone Function 4: Renders a structured dictionary into a clean console report."""
#     lines = []
#     lines.append("=" * 68)
#     lines.append(f"          SMART FITNESS SESSION REPORT - PARTICIPANT: {report_dict['participant_id']}")
#     lines.append("=" * 68)

#     lines.append(f"CLASSIFICATION      : {report_dict['classification'].upper()}")
#     lines.append(f"EXPLANATION         : {report_dict['explanation']}")
#     lines.append("-" * 68)

#     q = report_dict["data_quality"]
#     lines.append("DATA QUALITY METRICS:")
#     lines.append(f"  • Total Windows Received : {q['total_observations']}")
#     lines.append(f"  • Usable Windows Accepted: {q['usable_observations']}")
#     lines.append(f"  • Invalid Windows Flagged: {q['rejected_observations']}")
#     lines.append(f"  • Data Usability Rate    : {q['usable_percentage']}%")
#     lines.append("-" * 68)

#     if report_dict["classification"] != "insufficient data":
#         lines.append("FEATURE SUMMARY STATISTICS (Usable Data Only):")
#         for feature, stats in report_dict["summaries"].items():
#             name = feature.replace("_", " ").title()
#             lines.append(f"  • {name:<18}: Mean={stats['mean']:<6} Min={stats['min']:<6} Max={stats['max']:<6} Std={stats['std_dev']}")

#         lines.append("-" * 68)
#         comp = report_dict["baseline_comparison"]
#         lines.append("BASELINE REFERENCE COMPARISON:")
#         lines.append(f"  • Heart Rate Baseline : {comp['baseline_hr']} bpm -> Avg: {comp['session_avg_hr']} bpm (Diff: {comp['hr_delta']:+0.2f} bpm, {comp['hr_percent_change']:+0.1f}%)")
#         lines.append(f"  • Temperature Baseline: {comp['baseline_temp']}°C -> Avg: {comp['session_avg_temp']}°C (Diff: {comp['temp_delta']:+0.2f}°C)")
#         lines.append(f"  • Skin Resp Baseline  : {comp['baseline_skin']} -> Avg: {comp['session_avg_skin']} (Diff: {comp['skin_delta']:+0.2f})")

#     lines.append("=" * 68)
#     return "\n".join(lines)



def calculate_summary_statistics(data_list: list) -> dict:
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

    if avg_hr_early > baseline_hr + 15 and hr_decline_ratio >= 0.15 and act_decline >= 0.15:
        reason = (f"Heart rate dropped {hr_decline_ratio * 100:.1f}% ({avg_hr_early:.1f} → {avg_hr_late:.1f} bpm) "
                  f"and activity declined by {act_decline:.2f}.")
        return True, reason

    return False, f"No significant recovery trajectory detected (HR drop: {hr_decline_ratio * 100:.1f}%, Activity drop: {act_decline:.2f})."











# analyzer