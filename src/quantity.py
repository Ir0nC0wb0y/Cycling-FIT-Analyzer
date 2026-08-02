from dataclasses import dataclass

@dataclass(frozen=True)
class Quantity:
    value: any
    unit: str

    def __format__(self, format_spec):
        if format_spec.endswith("u"):
            # Format with units
            value_format = format_spec[:-1]
            return f"{format(self.value, value_format)} {self.unit}"

        # Normal numeric formatting
        return format(self.value, format_spec)
    def __str__(self):
        return f"{self.value} {self.unit}"