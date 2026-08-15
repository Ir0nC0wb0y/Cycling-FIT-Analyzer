import fitdecode


def inspect_altitude(filename):

    print(f"Inspecting: {filename}")
    print("-" * 100)

    with fitdecode.FitReader(filename) as fit:

        for frame in fit:

            if not isinstance(frame, fitdecode.FitDataMessage):
                continue

            for field in frame.fields:

                if (
                    "alt" in field.name.lower()
                    or "elev" in field.name.lower()
                ):

                    print(
                        f"message={frame.name:<20} "
                        f"field={field.name:<25} "
                        f"value={field.value!r:<15} "
                        f"units={field.units!r}"
                    )


inspect_altitude("data/20260813.fit")