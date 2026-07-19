from pathlib import Path
import fitdecode

# Path to the project directory (where main.py lives)
PROJECT_DIR = Path(__file__).parent

fit_file = PROJECT_DIR / "FitFiles" /  "20260716054447_10886424.fit"

print(fit_file)

with fitdecode.FitReader(fit_file) as fit:
    for frame in fit:
        if (
            isinstance(frame, fitdecode.FitDataMessage)
            and frame.name == "record"
        ):
            timestamp = frame.get_value("timestamp")
            speed = frame.get_value("speed")
            hr = frame.get_value("heart_rate")

            print(timestamp, speed, hr)