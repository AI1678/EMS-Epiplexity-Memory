"""
元认知系统

Phase 4: 记忆的自我评估、价值预测和主动遗忘
基于Epiplexity理论，实现记忆的元认知管理
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import numpy as np


class MemoryQuality(Enum):
    """记忆质量等级"""
    CRITICAL = "critical"      # 关键记忆（永不遗忘）
    HIGH = "high"              # 高价值记忆
    MEDIUM = "medium"          # 中等价值
    LOW = "low"                # 低价值（可遗忘）
    GARBAGE = "garbage"        # 垃圾记忆（立即清除）


@dataclass
class MemoryEvaluation:
    """记忆评估结果"""
    memory_id: str
    quality: MemoryQuality
    value_score: float          # 0-1 价值分数
    retention_probability: float  # 0-1 保留概率
    forget_after: Optional[timedelta]  # 何时遗忘
    reasons: List[str]          # 评估理由
    
    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "quality": self.quality.value,
            "value_score": self.value_score,
            "retention_probability": self.retention_probability,
            "forget_after": str(self.forget_after) if self.forget_after else None,
            "reasons": self.reasons
        }


class MemoryValuePredictor:
    """
    记忆价值预测器
    
    预测记忆的未来价值，基于：
    - 当前Epiplexity
    - 访问历史
    - 时间衰减
    - 与其他记忆的关系
    """
    
    def __init__(
        self,
        decay_half_life: timedelta = timedelta(days=7),
        access_weight: float = 0.3,
        epiplexity_weight: float = 0.4,
        relation_weight: float = 0.2,
        recency_weight: float = 0.1
    ):
        self.decay_half_life = decay_half_life
        self.weights = {
            "access": access_weight,
            "epiplexity": epiplexity_weight,
            "relation": relation_weight,
            "recency": recency_weight
        }
    
    def predict_value(
        self,
        memory: Dict[str, Any],
        all_memories: Dict[str, Dict] = None
    ) -> float:
        """
        预测记忆的未来价值
        
        Returns:
            0-1 之间的价值分数
        """
        scores = []
        
        # 1. Epiplexity分数 (0-1)
        epiplexity_score = memory.get("epiplexity_score", 0.5)
        scores.append(("epiplexity", epiplexity_score))
        
        # 2. 访问频率分数
        access_score = self._compute_access_score(memory)
        scores.append(("access", access_score))
        
        # 3. 关系丰富度分数
        relation_score = self._compute_relation_score(memory, all_memories or {})
        scores.append(("relation", relation_score))
        
        # 4. 时间新鲜度分数
        recency_score = self._compute_recency_score(memory)
        scores.append(("recency", recency_score))
        
        # 加权求和
        total_value = sum(
            score * self.weights[name]
            for name, score in scores
        )
        
        return min(1.0, max(0.0, total_value))
    
    def _compute_access_score(self, memory: Dict) -> float:
        """计算访问频率分数"""
        access_count = memory.get("access_count", 0)
        
        # 使用对数缩放，避免高频访问主导
        if access_count == 0:
            return 0.1
        
        return min(1.0, math.log10(access_count + 1) / 2)
    
    def _compute_relation_score(
        self,
        memory: Dict,
        all_memories: Dict[str, Dict]
    ) -> float:
        """计算关系丰富度分数"""
        structure = memory.get("structure", {})
        
        # 统计关系数量
        relation_count = len(structure.get("relations", []))
        entity_count = len(structure.get("entities", []))
        
        # 与其他记忆的连接数
        connection_count = 0
        mem_id = memory.get("id", "")
        
        for other_id, other_mem in all_memories.items():
            if other_id == mem_id:
                continue
            
            other_structure = other_mem.get("structure", {})
            other_entities = {e.get("text", "") for e in other_structure.get("entities", [])}
            my_entities = {e.get("text", "") for e in structure.get("entities", [])}
            
            if other_entities & my_entities:  # 有共同实体
                connection_count += 1
        
        # 综合分数
        score = (
            min(0.4, relation_count * 0.1) +
            min(0.3, entity_count * 0.05) +
            min(0.3, connection_count * 0.05)
        )
        
        return score
    
    def _compute_recency_score(self, memory: Dict) -> float:
        """计算时间新鲜度分数"""
        last_accessed = memory.get("last_accessed")
        created = memory.get("timestamp")
        
        if not last_accessed and not created:
            return 0.5
        
        # 使用最近的时间
        time_str = last_accessed or created
        try:
            last_time = datetime.fromisoformat(time_str)
            now = datetime.now()
            age = now - last_time
            
            # 指数衰减
            half_life_seconds = self.decay_half_life.total_seconds()
            age_seconds = age.total_seconds()
            
            decay = math.exp(-0.693 * age_seconds / half_life_seconds)
            return decay
        except:
            return 0.5


class MemoryQualityEvaluator:
    """
    记忆质量评估器
    
    评估记忆质量等级，决定保留策略
    """
    
    def __init__(
        self,
        critical_keywords: List[str] = None,
        garbage_keywords: List[str] = None
    ):
        self.critical_keywords = critical_keywords or [
            "身份", "IDENTITY", "密码", "password",
            "重要", "critical", "核心", "core",
            "陈学东", "陈博士", "OpenClaw-Rft"
        ]
        
        self.garbage_keywords = garbage_keywords or [
            "测试", "test", "临时", "temp",
            "随便", "random", "无关"
        ]
    
    def evaluate(
        self,
        memory: Dict[str, Any],
        value_score: float
    ) -> MemoryEvaluation:
        """
        评估记忆质量
        
        Returns:
            MemoryEvaluation: 评估结果
        """
        memory_id = memory.get("id", "unknown")
        content = memory.get("content", "")
        reasons = []
        
        # 检查关键记忆
        if self._is_critical_memory(memory, content):
            return MemoryEvaluation(
                memory_id=memory_id,
                quality=MemoryQuality.CRITICAL,
                value_score=1.0,
                retention_probability=1.0,
                forget_after=None,
                reasons=["包含关键信息，永不遗忘"]
            )
        
        # 检查垃圾记忆
        if self._is_garbage_memory(memory, content):
            return MemoryEvaluation(
                memory_id=memory_id,
                quality=MemoryQuality.GARBAGE,
                value_score=0.0,
                retention_probability=0.0,
                forget_after=timedelta(hours=1),
                reasons=["低质量内容，建议立即清除"]
            )
        
        # 基于价值分数确定质量等级
        if value_score >= 0.8:
            quality = MemoryQuality.HIGH
            retention_prob = 0.95
            forget_after = None
            reasons.append(f"高价值记忆 (score: {value_score:.2f})")
            
        elif value_score >= 0.5:
            quality = MemoryQuality.MEDIUM
            retention_prob = 0.7
            forget_after = timedelta(days=30)
            reasons.append(f"中等价值记忆 (score: {value_score:.2f})")
            
        else:
            quality = MemoryQuality.LOW
            retention_prob = 0.3
            forget_after = timedelta(days=7)
            reasons.append(f"低价值记忆 (score: {value_score:.2f})")
        
        # 添加额外理由
        epiplexity = memory.get("epiplexity_score", 0)
        if epiplexity > 0.8:
            reasons.append(f"高Epiplexity ({epiplexity:.2f})")
        
        access_count = memory.get("access_count", 0)
        if access_count > 10:
            reasons.append(f"高频访问 ({access_count}次)")
        
        return MemoryEvaluation(
            memory_id=memory_id,
            quality=quality,
            value_score=value_score,
            retention_probability=retention_prob,
            forget_after=forget_after,
            reasons=reasons
        )
    
    def _is_critical_memory(self, memory: Dict, content: str) -> bool:
        """检查是否为关键记忆"""
        # 检查重要性标记（优先）
        if memory.get("importance", 1.0) > 0.95:
            return True
        
        # 关键词检查（需要完整匹配或作为独立词）
        content_lower = content.lower()
        
        for keyword in self.critical_keywords:
            kw_lower = keyword.lower()
            # 检查是否作为独立词出现
            if f" {kw_lower} " in f" {content_lower} " or \
               content_lower.startswith(kw_lower + " ") or \
               content_lower.endswith(" " + kw_lower) or \
               content_lower == kw_lower:
                return True
        
        return False
    
    def _is_garbage_memory(self, memory: Dict, content: str) -> bool:
        """检查是否为垃圾记忆"""
        content_lower = content.lower()
        
        for keyword in self.garbage_keywords:
            if keyword.lower() in content_lower:
                return True
        
        # 内容过短
        if len(content) < 10:
            return True
        
        # Epiplexity极低
        if memory.get("epiplexity_score", 0.5) < 0.1:
            return True
        
        return False


class ActiveForgetting:
    """
    主动遗忘系统
    
    基于评估结果，主动遗忘低价值记忆
    """
    
    def __init__(
        self,
        garbage_threshold: float = 0.1,
        low_value_threshold: float = 0.3
    ):
        self.garbage_threshold = garbage_threshold
        self.low_value_threshold = low_value_threshold
        self.forget_log: List[Dict] = []
    
    def should_forget(
        self,
        evaluation: MemoryEvaluation,
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        判断是否应该遗忘
        
        Returns:
            True if should forget
        """
        if current_time is None:
            current_time = datetime.now()
        
        # 关键记忆永不遗忘
        if evaluation.quality == MemoryQuality.CRITICAL:
            return False
        
        # 垃圾记忆立即遗忘
        if evaluation.quality == MemoryQuality.GARBAGE:
            return True
        
        # 检查是否超过保留期限
        if evaluation.forget_after:
            # 这里需要知道记忆创建时间，简化处理
            # 实际实现中应该从记忆中获取
            retention_prob = evaluation.retention_probability
            
            # 基于概率的遗忘决策
            import random
            return random.random() > retention_prob
        
        return False
    
    def forget(
        self,
        memory_id: str,
        evaluation: MemoryEvaluation,
        memories: Dict[str, Dict]
    ) -> bool:
        """
        执行遗忘
        
        Returns:
            True if successfully forgotten
        """
        if memory_id not in memories:
            return False
        
        # 记录遗忘日志
        self.forget_log.append({
            "memory_id": memory_id,
            "forgotten_at": datetime.now().isoformat(),
            "quality": evaluation.quality.value,
            "value_score": evaluation.value_score,
            "reasons": evaluation.reasons
        })
        
        # 删除记忆
        del memories[memory_id]
        
        return True
    
    def get_forget_stats(self) -> Dict[str, Any]:
        """获取遗忘统计"""
        if not self.forget_log:
            return {"total_forgotten": 0}
        
        quality_counts = {}
        for entry in self.forget_log:
            q = entry["quality"]
            quality_counts[q] = quality_counts.get(q, 0) + 1
        
        return {
            "total_forgotten": len(self.forget_log),
            "quality_distribution": quality_counts,
            "avg_value_score": sum(e["value_score"] for e in self.forget_log) / len(self.forget_log)
        }


class MetacognitiveManager:
    """
    元认知管理器
    
    整合价值预测、质量评估和主动遗忘
    """
    
    def __init__(
        self,
        evaluation_interval: timedelta = timedelta(hours=6)
    ):
        self.value_predictor = MemoryValuePredictor()
        self.quality_evaluator = MemoryQualityEvaluator()
        self.active_forgetting = ActiveForgetting()
        self.evaluation_interval = evaluation_interval
        self.last_evaluation: Optional[datetime] = None
        self.evaluation_history: List[Dict] = []
    
    def evaluate_all(
        self,
        memories: Dict[str, Dict[str, Any]]
    ) -> Dict[str, MemoryEvaluation]:
        """
        评估所有记忆
        
        Returns:
            {memory_id: MemoryEvaluation}
        """
        self.last_evaluation = datetime.now()
        evaluations = {}
        
        for mem_id, memory in memories.items():
            # 预测价值
            value_score = self.value_predictor.predict_value(memory, memories)
            
            # 评估质量
            evaluation = self.quality_evaluator.evaluate(memory, value_score)
            evaluations[mem_id] = evaluation
        
        # 记录历史
        self.evaluation_history.append({
            "timestamp": self.last_evaluation.isoformat(),
            "memory_count": len(memories),
            "evaluations": {k: v.to_dict() for k, v in evaluations.items()}
        })
        
        return evaluations
    
    def run_forgetting_cycle(
        self,
        memories: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        运行遗忘周期
        
        Returns:
            遗忘结果统计
        """
        # 评估所有记忆
        evaluations = self.evaluate_all(memories)
        
        # 决定遗忘哪些
        to_forget = []
        for mem_id, evaluation in evaluations.items():
            if self.active_forgetting.should_forget(evaluation):
                to_forget.append((mem_id, evaluation))
        
        # 执行遗忘
        forgotten = []
        for mem_id, evaluation in to_forget:
            if self.active_forgetting.forget(mem_id, evaluation, memories):
                forgotten.append(mem_id)
        
        return {
            "evaluated": len(evaluations),
            "marked_for_forgetting": len(to_forget),
            "actually_forgotten": len(forgotten),
            "forgotten_ids": forgotten,
            "forget_stats": self.active_forgetting.get_forget_stats()
        }
    
    def get_memory_report(
        self,
        memories: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        生成记忆报告
        
        展示记忆系统的元认知状态
        """
        evaluations = self.evaluate_all(memories)
        
        quality_distribution = {}
        value_distribution = {"high": 0, "medium": 0, "low": 0}
        
        for evaluation in evaluations.values():
            q = evaluation.quality.value
            quality_distribution[q] = quality_distribution.get(q, 0) + 1
            
            if evaluation.value_score >= 0.7:
                value_distribution["high"] += 1
            elif evaluation.value_score >= 0.4:
                value_distribution["medium"] += 1
            else:
                value_distribution["low"] += 1
        
        return {
            "total_memories": len(memories),
            "quality_distribution": quality_distribution,
            "value_distribution": value_distribution,
            "avg_value_score": sum(e.value_score for e in evaluations.values()) / len(evaluations) if evaluations else 0,
            "critical_memories": quality_distribution.get("critical", 0),
            "garbage_memories": quality_distribution.get("garbage", 0),
            "last_evaluation": self.last_evaluation.isoformat() if self.last_evaluation else None
        }
