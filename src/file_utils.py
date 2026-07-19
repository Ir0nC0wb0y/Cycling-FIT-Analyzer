from pathlib import Path
import config


def find_input_file(filename=None):
    """
    Locate a FIT file.

    Cases:
      1. Explicit path
      2. Filename only
      3. No filename
    """

    # Convert configured directories to Path objects
    search_dirs = [
        Path(directory).expanduser()
        for directory in config.FIT_DEFAULT_DIRS
    ]

    #
    # Case 1 / 2
    #
    if filename:

        path = Path(filename).expanduser()

        # -------------------------------------------------
        # Case 1: User supplied a valid path
        # -------------------------------------------------
        if path.exists():
            return path

        # -------------------------------------------------
        # Case 2: User supplied only a filename
        # -------------------------------------------------
        if len(path.parts) == 1:

            for directory in search_dirs:

                if not directory.exists():
                    continue

                candidate = directory / path.name

                if candidate.exists():
                    return candidate

            raise FileNotFoundError(
                f"Could not find '{path.name}' in any default directory."
            )

        raise FileNotFoundError(
            f"File '{filename}' does not exist."
        )

    #
    # Case 3: No filename supplied
    #
    found = []

    for directory in search_dirs:

        if not directory.exists():
            continue

        found.extend(directory.glob("*.fit"))

    if len(found) == 0:
        raise FileNotFoundError(
            "No FIT files found in the default directories."
        )

    if len(found) == 1:
        return found[0]

    print("Multiple FIT files found:\n")

    for i, file in enumerate(found, start=1):
        print(f"{i:2}) {file.name}")

    while True:
        try:
            choice = int(input("\nSelect file: "))

            if 1 <= choice <= len(found):
                return found[choice - 1]

        except ValueError:
            pass

        print("Invalid selection.")