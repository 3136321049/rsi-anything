"""Plugins: judges, coding agents and search strategies that live in other packages.

Built-in names are registered by their own modules. A package adds more through entry points
in its pyproject.toml, and rsi.yaml then uses the name like a built-in one:

    [project.entry-points."rsi_anything.judges"]
    vision = "my_package.vision:VisionJudge"    # VisionJudge(spec) -> Judge;   rsi.yaml: judge: {type: vision}

    [project.entry-points."rsi_anything.agents"]
    aider = "my_package.aider:make_agent"       # make_agent(spec, allow_commands) -> Agent, or a CLISpec
                                                #                                 rsi.yaml: agent: {use: aider}
    [project.entry-points."rsi_anything.strategies"]
    best-of-3 = "my_package.search:BestOfThree" # BestOfThree() -> Strategy;    rsi.yaml: strategy: best-of-3

Code can also register directly, for a test or a local script: `JUDGES.register("vision", VisionJudge)`.
A plugin judge receives every key of its rsi.yaml block that rsi does not know in `spec.options`.
Nothing is imported until a contract asks for that name.
"""
from __future__ import annotations

from importlib import metadata
from typing import Any, Callable, Optional, Union


class PluginError(ValueError):
    """A name in rsi.yaml that nothing provides, or a plugin that failed to load."""


def _dist(point) -> str:
    name = getattr(getattr(point, "dist", None), "name", None)
    return f"package {name}" if name else "package"


class Registry:
    def __init__(self, group: str, what: str):
        self.group, self.what = group, what
        self._items: dict[str, Any] = {}
        self._origins: dict[str, str] = {}

    def register(self, name: str, item: Any = None, origin: str = "registered") -> Union[Any, Callable[[Any], Any]]:
        """Add `item` under `name`; without an item, works as a decorator."""
        if item is None:
            return lambda obj: self.register(name, obj, origin)
        self._items[name] = item
        self._origins[name] = origin
        return item

    def _points(self) -> list:
        try:
            found = metadata.entry_points()
        except Exception:  # a broken installed package must not break rsi
            return []
        return list(found.select(group=self.group) if hasattr(found, "select") else found.get(self.group, []))

    def find(self, name: str) -> Optional[Any]:
        if name in self._items:
            return self._items[name]
        for point in self._points():
            if point.name == name:
                try:
                    item = point.load()
                except Exception as exc:
                    raise PluginError(f"{self.what} {name!r} from {point.value} failed to load: {exc}") from exc
                return self.register(name, item, _dist(point))
        return None

    def get(self, name: str) -> Any:
        item = self.find(name)
        if item is None:
            raise PluginError(f"unknown {self.what} {name!r}; available: {', '.join(self.names()) or 'none'}")
        return item

    def names(self) -> list[str]:
        return list(dict.fromkeys([*self._items, *(point.name for point in self._points())]))

    def origins(self) -> dict[str, str]:
        found = dict(self._origins)
        for point in self._points():
            found.setdefault(point.name, _dist(point))
        return found
