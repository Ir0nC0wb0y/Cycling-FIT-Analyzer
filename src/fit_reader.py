from pathlib import Path
import config

import fitdecode

def get_available_fields(filename, display=False):
    """
    Read the record headers and their units
    """
    fields = []

    with fitdecode.FitReader(filename) as fit:
        for frame in fit:
            if (
                isinstance(frame, fitdecode.FitDataMessage)
                and frame.name == "record"
            ):
                for field in frame.fields:
                    fields.append(
                        (field.name, field.units)
                    )
                break

    if display:
        print("Field              Units")
        print("------------------------")
        for name, units in fields:
            print(f"{name:20} {units}")

    return fields

def clean_fit_value(value):
    if value is None:
        return config.MISSING_DATA_VALUE
    return value

def load_fit(filename):
    """
    Read a FIT file and return a list of record dictionaries.
    """

    print(f"Loading {filename} ...")

    path = Path(filename)

    if not path.exists():
        raise FileNotFoundError(f"Could not find '{filename}'")

    records = []

    with fitdecode.FitReader(path) as fit:

        for frame in fit:

            if (
                isinstance(frame, fitdecode.FitDataMessage)
                and frame.name == "record"
            ):
            
                record = {}

                for field in frame.fields:
                    if field.name in config.FIT_USE_FIELDS:
                        #record[field.name] = field.value
                        record[field.name] = clean_fit_value(field.value)

                records.append(record)

    print(f"Loaded {len(records)} records.")

    return records


