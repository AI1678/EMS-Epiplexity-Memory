"""
自动记忆巩固系统

Phase 3: 睡眠模式记忆整合
基于Epiplexity理论，实现跨时间模式提取和记忆压缩
"""

import json
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib


@dataclass
class Pattern:
    """提取的模式"""
    pattern_type: str  # "entity", "relation", "template", "topic"
    content: Any
    frequency: int
    confidence: float
    source_memories: List[str]  # 来源记忆ID列表
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AbstractMemory:
    """抽象记忆（模式聚合）"""
    id: str
    created_at: str
    pattern_type: str
    summary: str
    patterns: List[Pattern]
    source_count: int
    epiplexity_score: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "pattern_type": self.pattern_type,
            "summary": self.summary,
            "patterns": [p.to_dict() for p in self.patterns],
            "source_count": self.source_count,
            "epiplexity_score": self.epiplexity_score,
            "metadata": self.metadata
        }


class PatternMiner:
    """
    模式挖掘器
    
    从多个记忆中提取共同模式
    """
    
    def __init__(self, min_frequency: int = 2, min_confidence: float = 0.6):
        self.min_frequency = min_frequency
        self.min_confidence = min_confidence
    
    def mine_patterns(
        self,
        memories: List[Dict[str, Any]]
    ) -> Dict[str, List[Pattern]]:
        """
        挖掘记忆中的模式
        
        Returns:
            {
                "entities": [Pattern, ...],
                "relations": [Pattern, ...],
                "templates": [Pattern, ...],
                "topics": [Pattern, ...]
            }
        """
        patterns = {
            "entities": self._mine_entity_patterns(memories),
            "relations": self._mine_relation_patterns(memories),
            "templates": self._mine_template_patterns(memories),
            "topics": self._mine_topic_patterns(memories)
        }
        
        return patterns
    
    def _mine_entity_patterns(self, memories: List[Dict]) -> List[Pattern]:
        """挖掘实体模式"""
        entity_counts = defaultdict(lambda: {"count": 0, "sources": [], "types": set()})
        
        for memory in memories:
            mem_id = memory.get("id", "unknown")
            structure = memory.get("structure", {})
            
            for entity in structure.get("entities", []):
                key = (entity.get("type", "UNKNOWN"), entity.get("text", ""))
                entity_counts[key]["count"] += 1
                entity_counts[key]["sources"].append(mem_id)
                entity_counts[key]["types"].add(entity.get("type", "UNKNOWN"))
        
        patterns = []
        for (etype, etext), data in entity_counts.items():
            if data["count"] >= self.min_frequency:
                confidence = min(1.0, data["count"] / len(memories) + 0.3)
                patterns.append(Pattern(
                    pattern_type="entity",
                    content={"type": etype, "text": etext},
                    frequency=data["count"],
                    confidence=confidence,
                    source_memories=data["sources"]
                ))
        
        return sorted(patterns, key=lambda p: p.frequency, reverse=True)
    
    def _mine_relation_patterns(self, memories: List[Dict]) -> List[Pattern]:
        """挖掘关系模式"""
        relation_counts = defaultdict(lambda: {"count": 0, "sources": []})
        
        for memory in memories:
            mem_id = memory.get("id", "unknown")
            structure = memory.get("structure", {})
            
            for relation in structure.get("relations", []):
                key = (
                    relation.get("type", "UNKNOWN"),
                    relation.get("source", ""),
                    relation.get("target", "")
                )
                relation_counts[key]["count"] += 1
                relation_counts[key]["sources"].append(mem_id)
        
        patterns = []
        for (rtype, rsource, rtarget), data in relation_counts.items():
            if data["count"] >= self.min_frequency:
                confidence = min(1.0, data["count"] / len(memories) + 0.2)
                patterns.append(Pattern(
                    pattern_type="relation",
                    content={
                        "type": rtype,
                        "source": rsource,
                        "target": rtarget
                    },
                    frequency=data["count"],
                    confidence=confidence,
                    source_memories=data["sources"]
                ))
        
        return sorted(patterns, key=lambda p: p.frequency, reverse=True)
    
    def _mine_template_patterns(self, memories: List[Dict]) -> List[Pattern]:
        """挖掘模板模式"""
        template_counts = defaultdict(lambda: {"count": 0, "sources": []})
        
        for memory in memories:
            mem_id = memory.get("id", "unknown")
            structure = memory.get("structure", {})
            
            for template in structure.get("templates", []):
                template_counts[template]["count"] += 1
                template_counts[template]["sources"].append(mem_id)
        
        patterns = []
        for template, data in template_counts.items():
            if data["count"] >= self.min_frequency:
                confidence = min(1.0, data["count"] / len(memories) + 0.4)
                patterns.append(Pattern(
                    pattern_type="template",
                    content=template,
                    frequency=data["count"],
                    confidence=confidence,
                    source_memories=data["sources"]
                ))
        
        return sorted(patterns, key=lambda p: p.frequency, reverse=True)
    
    def _mine_topic_patterns(self, memories: List[Dict]) -> List[Pattern]:
        """挖掘主题模式"""
        topic_counts = defaultdict(lambda: {"count": 0, "sources": []})
        
        for memory in memories:
            mem_id = memory.get("id", "unknown")
            structure = memory.get("structure", {})
            
            for topic in structure.get("topics", []):
                topic_counts[topic]["count"] += 1
                topic_counts[topic]["sources"].append(mem_id)
        
        patterns = []
        for topic, data in topic_counts.items():
            if data["count"] >= self.min_frequency:
                confidence = min(1.0, data["count"] / len(memories) + 0.3)
                patterns.append(Pattern(
                    pattern_type="topic",
                    content=topic,
                    frequency=data["count"],
                    confidence=confidence,
                    source_memories=data["sources"]
                ))
        
        return sorted(patterns, key=lambda p: p.frequency, reverse=True)


class MemoryCompressor:
    """
    记忆压缩器
    
    将多个相关记忆压缩为抽象记忆
    """
    
    def __init__(self, compression_ratio: float = 0.5):
        self.compression_ratio = compression_ratio
    
    def compress(
        self,
        memories: List[Dict[str, Any]],
        patterns: Dict[str, List[Pattern]]
    ) -> AbstractMemory:
        """
        压缩记忆为抽象记忆
        
        Args:
            memories: 待压缩的记忆列表
            patterns: 挖掘出的模式
            
        Returns:
            AbstractMemory: 抽象记忆
        """
        # 生成摘要
        summary = self._generate_summary(memories, patterns)
        
        # 计算Epiplexity（抽象记忆具有高Epiplexity）
        epiplexity = self._compute_abstract_epiplexity(patterns)
        
        # 收集所有模式
        all_patterns = []
        for pattern_list in patterns.values():
            all_patterns.extend(pattern_list)
        
        # 按置信度排序
        all_patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        return AbstractMemory(
            id=self._generate_id(summary),
            created_at=datetime.now().isoformat(),
            pattern_type="consolidated",
            summary=summary,
            patterns=all_patterns[:20],  # 保留top 20模式
            source_count=len(memories),
            epiplexity_score=epiplexity,
            metadata={
                "compression_ratio": self.compression_ratio,
                "source_memory_ids": [m.get("id") for m in memories],
                "pattern_types": list(patterns.keys())
            }
        )
    
    def _generate_summary(
        self,
        memories: List[Dict],
        patterns: Dict[str, List[Pattern]]
    ) -> str:
        """生成抽象摘要"""
        # 提取关键主题
        top_topics = patterns.get("topics", [])[:3]
        topic_names = [p.content for p in top_topics]
        
        # 提取关键实体
        top_entities = patterns.get("entities", [])[:5]
        entity_names = [p.content.get("text", "") for p in top_entities]
        
        # 生成摘要文本
        summary_parts = []
        
        if topic_names:
            summary_parts.append(f"主题: {', '.join(topic_names)}")
        
        if entity_names:
            summary_parts.append(f"关键实体: {', '.join(entity_names)}")
        
        summary_parts.append(f"基于{len(memories)}条记忆的抽象")
        
        return "; ".join(summary_parts)
    
    def _compute_abstract_epiplexity(
        self,
        patterns: Dict[str, List[Pattern]]
    ) -> float:
        """计算抽象记忆的Epiplexity"""
        scores = []
        
        # 模式丰富度
        total_patterns = sum(len(p) for p in patterns.values())
        scores.append(min(0.3, total_patterns * 0.05))
        
        # 平均置信度
        all_confidences = []
        for pattern_list in patterns.values():
            all_confidences.extend([p.confidence for p in pattern_list])
        
        if all_confidences:
            avg_confidence = sum(all_confidences) / len(all_confidences)
            scores.append(avg_confidence * 0.4)
        
        # 模式多样性
        pattern_types = len([p for p in patterns.values() if p])
        scores.append(pattern_types * 0.1)
        
        return min(1.0, sum(scores))
    
    def _generate_id(self, content: str) -> str:
        """生成唯一ID"""
        return f"abstract_{hashlib.md5(content.encode()).hexdigest()[:12]}"


class SleepConsolidator:
    """
    睡眠巩固器
    
    模拟睡眠时的记忆整合过程
    """
    
    def __init__(
        self,
        consolidation_interval: timedelta = timedelta(hours=24),
        min_memories_for_consolidation: int = 5
    ):
        self.consolidation_interval = consolidation_interval
        self.min_memories = min_memories_for_consolidation
        self.pattern_miner = PatternMiner()
        self.compressor = MemoryCompressor()
        self.last_consolidation: Optional[datetime] = None
    
    def should_consolidate(self, memory_count: int) -> bool:
        """检查是否应该进行巩固"""
        if memory_count < self.min_memories:
            return False
        
        if self.last_consolidation is None:
            return True
        
        time_since_last = datetime.now() - self.last_consolidation
        return time_since_last >= self.consolidation_interval
    
    def consolidate(
        self,
        l2_memories: Dict[str, Dict],
        l3_memories: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        执行睡眠巩固
        
        1. 聚类相关记忆
        2. 挖掘共同模式
        3. 压缩为抽象记忆
        4. 更新L3长期记忆
        
        Returns:
            巩固统计
        """
        self.last_consolidation = datetime.now()
        
        # 转换为列表
        l2_list = list(l2_memories.values())
        
        if len(l2_list) < self.min_memories:
            return {"status": "skipped", "reason": "insufficient_memories"}
        
        # 聚类记忆
        clusters = self._cluster_memories(l2_list)
        
        consolidation_results = []
        
        for cluster_id, cluster_memories in clusters.items():
            if len(cluster_memories) < self.min_memories:
                continue
            
            # 挖掘模式
            patterns = self.pattern_miner.mine_patterns(cluster_memories)
            
            # 压缩为抽象记忆
            abstract_memory = self.compressor.compress(cluster_memories, patterns)
            
            # 添加到L3
            l3_memories[abstract_memory.id] = abstract_memory.to_dict()
            
            consolidation_results.append({
                "abstract_id": abstract_memory.id,
                "source_count": len(cluster_memories),
                "pattern_count": sum(len(p) for p in patterns.values()),
                "epiplexity": abstract_memory.epiplexity_score
            })
        
        return {
            "status": "success",
            "consolidated_at": self.last_consolidation.isoformat(),
            "clusters_processed": len(clusters),
            "abstract_memories_created": len(consolidation_results),
            "details": consolidation_results
        }
    
    def _cluster_memories(
        self,
        memories: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """简单聚类（基于主题相似度）"""
        clusters = defaultdict(list)
        
        for memory in memories:
            # 使用主要主题作为聚类键
            topics = memory.get("structure", {}).get("topics", [])
            
            if topics:
                # 使用第一个主题作为聚类键
                cluster_key = topics[0]
            else:
                # 无主题的记忆放入"misc"
                cluster_key = "misc"
            
            clusters[cluster_key].append(memory)
        
        return dict(clusters)


# 向后兼容
class MemoryConsolidator(SleepConsolidator):
    """向后兼容的别名"""
    pass
