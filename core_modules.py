import statistics
from exceptions import InvalidIdentifierError

import re




class Metric:
    "Metric class represents a single observation within a session."
    
    MIN_SIGNAL_QUALITY = 0.60

    def __init__(self, timestamp: int, signal_quality: float):
        self.timestamp = timestamp
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
        Metric.is_valid() by adding domain-specific bounds checking and null validation.
        """
        if not super().is_valid():
            return False

        # Rejecting missing values 
        if None in (self.heart_rate, self.skin_response, self.temperature, self.activity_level):
            return False

        # here we are rejecting impossible range values
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
        """Extends Observation.get_summary with detailed fitness metrics."""
        base_summary = super().get_summary()
        if not self.is_valid():
            return f"{base_summary} | Status: INVALID"
        return f"{base_summary} | HR: {self.heart_rate} bpm | Activity: {self.activity_level} | Temp: {self.temperature}°C"



class Participant:
    """Represents a gym participant and encapsulates personal baseline measurements."""

    def __init__(self, participant_id: str, baseline_hr: float, baseline_skin: float, baseline_temp: float):
        # Regex validation for Participant ID format (P followed by 3 digits)
        if not re.match(r'^P\d{3}$', participant_id):
            raise InvalidIdentifierError(f"Invalid Participant ID format: {participant_id}")
            
        self.participant_id = participant_id
        # Private attributes
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
        """Factory constructor to instantiate Participant from raw generator dictionary."""
        return cls(
            participant_id=profile_dict.get("participant_id", "Unknown"),
            baseline_hr=profile_dict.get("baseline_heart_rate", 70.0),
            baseline_skin=profile_dict.get("baseline_skin_response", 1.5),
            baseline_temp=profile_dict.get("baseline_temperature", 32.0),
        )



class FitnessSession:
    """
    Represents a training session containing participant info and observation windows.
    """

    def __init__(self, session_id: str, participant: Participant, observations: list = None):
        #Regex validation for Session ID format (FIT-YYYY-NNN)
        if not re.match(r'^FIT-\d{4}-\d{3}$', session_id):
            raise InvalidIdentifierError(f"Invalid Session ID format: {session_id}")
            
        self.session_id = session_id  
        
        self.participant = participant  

        self.observations = observations if observations is not None else []  

    def add_observation(self, obs: FitnessObservation):
        """Add an observation instance to the session list."""
        self.observations.append(obs)

    def get_valid_observations(self) -> list:
        """Filter and return only valid observation objects."""
        return [obs for obs in self.observations if obs.is_valid()]

    def get_invalid_observations(self) -> list:
        """Filter and return only invalid/flagged observation objects."""
        return [obs for obs in self.observations if not obs.is_valid()]






