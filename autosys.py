import shutil, os, sys, platform
import sqllex  # type: ignore
from typing import Any
import httpx, usersettings  # type: ignore
from pathlib import Path
import math

__all__ = [
    "shutil",
    "os",
    "sys",
    "platform",
    "WINDOWS",
    "setting",
    "httpx",
    "sqllex",
    "Signal",
    "Path",
    "Mod",
    "SigProccessing"
]

_AUTOSYS_APP_ID = "autosys/user"
setting = usersettings.Settings(_AUTOSYS_APP_ID)

WINDOWS = platform.platform() == "win32"


class Signal:
    "signal object is used for storing unipolar activation values"

    _value: float | int

    def __init__(self, pow: float | int = 0) -> None:
        self.power = pow

    @property
    def power(self) -> float | int:
        return self._value

    @power.setter
    def power(self, new: float | int) -> None:
        assert 0 <= new <= 1, ValueError("signal power value must be between 0 and 1")
        self._value = new

    @property
    def activated(self) -> bool:
        return self.power == 1

    def __repr__(self):
        return f"{"+" if self.activated else "%"}{self.power}"

    def __add__(self, o: int | float | "Signal" | Any):
        assert isinstance(o, (int, float, Signal)), TypeError(
            "signal object can only be added to the following type: int, float, Signal"
        )
        if isinstance(o, (int, float)):
            p = o + self.power
            if p > 1:
                p = 1
            if p < 0:
                p = 0
            return Signal(p)
        else:
            p = o.power + self.power
            if p > 1:
                p = 1
            if p < 0:
                p = 0
            return Signal(p)

    def __sub__(self, o: int | float | "Signal" | Any):
        assert isinstance(o, (int, float, Signal)), TypeError(
            "signal object can only be subtracted to the following type: int, float, Signal"
        )
        if isinstance(o, (int, float)):
            p = o - self.power
            if p > 1:
                p = 1
            if p < 0:
                p = 0
            return Signal(p)
        else:
            p = o.power - self.power
            if p > 1:
                p = 1
            if p < 0:
                p = 0
            return Signal(p)

    def __mul__(self, o: int | float | "Signal" | Any):
        assert isinstance(o, (int, float, Signal)), TypeError(
            "signal object can only be multiplied to the following type: int, float, Signal"
        )
        if isinstance(o, (int, float)):
            p = o * self.power
            if p > 1:
                p = 1
            if p < 0:
                p = 0
            return Signal(p)
        else:
            p = o.power * self.power
            if p > 1:
                p = 1
            if p < 0:
                p = 0
            return Signal(p)

    def __div__(self, o: int | float | "Signal" | Any):
        assert isinstance(o, (int, float, Signal)), TypeError(
            "signal object can only be divided to the following type: int, float, Signal"
        )
        if isinstance(o, (int, float)):
            p = o / self.power
            if p > 1:
                p = 1
            if p < 0:
                p = 0
            return Signal(p)
        else:
            p = o.power / self.power
            if p > 1:
                p = 1
            if p < 0:
                p = 0
            return Signal(p)


class SigProccessing:
    @classmethod
    def modulate(cls, signal: Signal, modulator: Signal):
        return signal * modulator

    @classmethod
    def amp(cls, signal: Signal, strength: int):
        return signal * strength

    @classmethod
    def gain(cls, signal: Signal, g: float):
        return signal * g

    @classmethod
    def dcOffset(cls, signal: Signal, offset: float):
        return signal + offset

    @classmethod
    def clip(cls, signal: Signal, threshold: float):
        if signal.power > threshold:
            return Signal(threshold)
        return signal

    @classmethod
    def mix(cls, signalA: Signal, signalB: Signal):
        return signalA + signalB

    @classmethod
    def softClip(cls, signal: Signal, drive: float):
        return Signal(math.tanh((signal * drive).power))


class Mod:
    @classmethod
    def percent(cls, value: int | float, max: int | float, percent: int):
        return (value * percent) / max

    @classmethod
    def operator(cls, max: int | float, op: Signal, *, offset: int | float = 0):
        return (op + offset).power * max

    @classmethod
    def clamp(cls, value: int | float, min: int | float, max: int | float):
        if value < min:
            return min
        elif value > max:
            return max
        else:
            return value

    @classmethod
    def namelist(cls, names: list[str]):
        yield from names

    @classmethod
    def sine(
        cls,
        t: int | float,
        frequency: int | float = 440,
        phase: int | float = 0,
    ) -> Signal:
        return Signal((math.sin(2 * math.pi * frequency * t + phase) + 1) / 2)

    @classmethod
    def saw(
        cls,
        t: int | float,
        frequency: float | int = 440,
        phase: int | float = 0,
    ) -> Signal:
        return Signal((frequency * t + phase / (2 * math.pi)) % 1)

    @classmethod
    def square(
        cls,
        t: int | float,
        frequency: float | int = 440,
        phase: int | float = 0,
    ) -> Signal:
        return Signal(1 if math.sin(2 * math.pi * frequency * t + phase) >= 0 else 0)

    @classmethod
    def triangle(
        cls,
        t: int | float,
        frequency: float | int = 440,
        phase: int | float = 0,
    ) -> Signal:
        return Signal(abs(2 * ((frequency * t + phase / (2 * math.pi)) % 1) - 1))
