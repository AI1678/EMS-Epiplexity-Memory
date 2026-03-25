"""
EMS - Epiplexity Memory System
基于计算受限信息论的记忆系统

理论基础: arXiv:2601.03220
"""

__version__ = "0.1.0"
__author__ = "OpenClaw-Rft / 陈学东"

from .core import EpiplexityMemorySystem
from .encoder import StructureEncoder
from .retriever import HierarchicalRetriever
from .consolidator import MemoryConsolidator
from .dialogue_extractor import DialogueStructureExtractor, DialogueStructure
from .intelligent_retriever import (
    IntelligentRetriever,
    RetrievalResult,
    RetrievalPhase,
    ComputeBudgetManager,
    SemanticEncoder
)
from .sleep_consolidator import (
    SleepConsolidator,
    PatternMiner,
    MemoryCompressor,
    Pattern,
    AbstractMemory
)
from .metacognition import (
    MetacognitiveManager,
    MemoryValuePredictor,
    MemoryQualityEvaluator,
    ActiveForgetting,
    MemoryEvaluation,
    MemoryQuality
)
from .agi_integration import (
    AGIMemoryBridge,
    RCCEIntegration,
    DistributedMemoryNode,
    SelfImprovement,
    CognitiveState
)

__all__ = [
    "EpiplexityMemorySystem",
    "StructureEncoder",
    "HierarchicalRetriever",
    "MemoryConsolidator",
    "DialogueStructureExtractor",
    "DialogueStructure",
    "IntelligentRetriever",
    "RetrievalResult",
    "RetrievalPhase",
    "ComputeBudgetManager",
    "SemanticEncoder",
    "SleepConsolidator",
    "PatternMiner",
    "MemoryCompressor",
    "Pattern",
    "AbstractMemory",
    "MetacognitiveManager",
    "MemoryValuePredictor",
    "MemoryQualityEvaluator",
    "ActiveForgetting",
    "MemoryEvaluation",
    "MemoryQuality",
    "AGIMemoryBridge",
    "RCCEIntegration",
    "DistributedMemoryNode",
    "SelfImprovement",
    "CognitiveState"
]
