from pathlib import Path
import config

import fitdecode

#def get_available_fields(filename, display=False):
#    """
#    Read the record headers and their units
#    """
#    fields = []
#
#    with fitdecode.FitReader(filename) as fit:
#        for frame in fit:
#            if (
#                isinstance(frame, fitdecode.FitDataMessage)
#                and frame.name == "record"
#            ):
#                for field in frame.fields:
#                    fields.append(
#                        (field.name, field.units)
#                    )
#                break
#
#    if display:
#        print("Field              Units")
#        print("------------------------")
#        for name, units in fields:
#            print(f"{name:20} {units}")
#
#    return fields

def get_available_fields(filename, display=False):
    """
    Read the record fields and their units from a FIT file.

    Returns a list of (field_name, units) tuples.
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

        print("Fields available in FIT file")
        print("--------------------------------")

        for name, units in fields:

            if units:
                print(f"{name:25} {units}")
            else:
                print(f"{name:25}")

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
    units = {}

    fit_field_map = {
        definition["fit_field"]: name
        for name, definition in config.FIT_FIELDS.items()
    }

    

    with fitdecode.FitReader(path) as fit:

        for frame in fit:

            if (
                isinstance(frame, fitdecode.FitDataMessage)
                and frame.name == "record"
            ):

                record = {}

                for field in frame.fields:

                    if field.name in fit_field_map:

                        name = fit_field_map[field.name]

                        value = clean_fit_value(field.value)

                        record[name] = value
                        units[name] = field.units

                #print("RECORD KEYS:", record.keys())
                records.append(record)

    #print("FIT FIELD MAP:")
    #print(fit_field_map)

    #print("FIRST RECORD:")
    #print(records[0])

    #print("UNITS:")
    #print(units)

    print(f"Loaded {len(records)} records.")

    return records, units
