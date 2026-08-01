from time import perf_counter


class PerformanceLogger:

    def __init__(self):

        self._active = {}

        self._results = []


    def tic(self, name):
        """
        Start a timer.
        """

        self._active[name] = perf_counter()


    def toc(
        self,
        name,
        save=True,
        show=False
    ):
        """
        Stop a timer.

        Returns elapsed seconds.
        """

        if name not in self._active:
            raise KeyError(
                f"Timer '{name}' was never started."
            )

        elapsed = (
            perf_counter()
            - self._active[name]
        )

        del self._active[name]

        if save:

            self._results.append(
                {
                    "name": name,
                    "time": elapsed,
                }
            )

        if show:

            print(
                f"{name:<30}"
                f"{elapsed:8.3f} s"
            )

        return elapsed


    def report(
        self,
        clear=True,
        exclude_uncomplete=False
    ):
        """
        Print saved timing results.
        """

        print()
        print("Performance Report")
        print("-" * 50)

        total = 0

        for result in self._results:

            print(
                f"{result['name']:<30}"
                f"{result['time']:8.3f} s"
            )

            total += result["time"]

        if (
            not exclude_uncomplete
            and self._active
        ):

            print("-" * 50)

            for name in self._active:

                print(
                    f"{name:<30}"
                    "(running)"
                )

        print("-" * 50)

        print(
            f"{'Total':<30}"
            f"{total:8.3f} s"
        )

        if clear:

            self._results.clear()

            if not exclude_uncomplete:
                self._active.clear()