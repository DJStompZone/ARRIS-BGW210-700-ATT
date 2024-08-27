import traceback
from dataclasses import dataclass

@dataclass
class Config:
    url: str
    username: str
    password: str


class ConfigError(Exception):
    def __init__(self, message: str, tb: str):
        super().__init__(message)
        self.message = message
        self.traceback = tb

    def __str__(self):
        return f"ConfigError: {self.message}\nTraceback:\n{self.traceback}"

