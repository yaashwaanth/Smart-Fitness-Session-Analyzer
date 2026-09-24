
# Sample Data Loader Module.



from data_generator import available_scenarios, generate_fitness_data


def load_sample_session(scenario_name="moderate_activity", seed=42, number_of_windows=10):
    """
    Fetch raw sample fitness data from generator and return both raw
    dictionaries and processed metadata.
    """
    profile, raw_observations = generate_fitness_data(
        participant_id="P_SAMPLE",
        scenario=scenario_name,
        seed=seed,
        number_of_windows=number_of_windows,
    )
    return profile, raw_observations


def inspect_sample_data():
    """Prints a quick breakdown of available sample data across scenarios."""
    print("Available Generator Scenarios:", available_scenarios())
    for scenario in available_scenarios():
        profile, obs = load_sample_session(scenario_name=scenario, number_of_windows=6)
        print(f"\nScenario: {scenario}")
        print("  Profile Baseline HR:", profile["baseline_heart_rate"])
        print("  First Observation Sample:", obs[0])


if __name__ == "__main__":
    inspect_sample_data()