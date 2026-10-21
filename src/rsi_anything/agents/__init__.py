"""Agents produce one candidate change per round. See `base.Agent`."""
from __future__ import annotations

from .base import Agent, AgentResult
from .registry import CLI_AGENTS, detect, make_agent

__all__ = ["Agent", "AgentResult", "CLI_AGENTS", "detect", "make_agent"]
