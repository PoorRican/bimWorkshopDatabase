from dataclasses import dataclass


@dataclass
class Parameter:
    name: str
    values: list[str]
