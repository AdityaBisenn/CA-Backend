# app/ram/__init__.py
"""
RAM Cognitive Framework
Resilient Reasoning, Adaptive Learning, and Meta-Cognition for CA firm automation
"""

from .ram_service import RAMOrchestrationService, get_ram_service
from .cognitive_core.reasoning_engine import RAMCognitiveEngine
from .adaptive_core.heuristic_memory import AdaptiveMemoryService
from .reflection_core.meta_cognition import MetaCognitionEngine

__all__ = [
    "RAMOrchestrationService",
    "get_ram_service", 
    "RAMCognitiveEngine",
    "AdaptiveMemoryService",
    "MetaCognitionEngine"
]