"""
智能检索引擎

Phase 2: 增强版分层检索系统
基于Epiplexity理论，实现计算预算内的最优检索
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from difflib import SequenceMatcher
from dataclasses import dataclass
from enum import Enum
import hashlib


class RetrievalPhase(Enum):
    """检索阶段"""
    L1_FAST = "l1_fast"           # 工作记忆快速匹配
    L2_STRUCTURE = "l2_structure"  # 短期记忆结构匹配
    L3_SEMANTIC = "l3_semantic"    # 长期记忆语义匹配


@dataclass
class RetrievalResult:
    """检索结果"""
    memory: Dict[str, Any]
    score: float
    phase: RetrievalPhase
    match_details: Dict[str, Any]


class ComputeBudgetManager:
    """
    计算预算管理器
    
    根据Epiplexity理论，在有限计算预算内优化检索
    """
    
    def __init__(self, total_budget: int):
        self.total_budget = total_budget
        self.used_budget = 0
        self.phase_budgets = {
            RetrievalPhase.L1_FAST: int(total_budget * 0.1),      # 10%给L1
            RetrievalPhase.L2_STRUCTURE: int(total_budget * 0.3),  # 30%给L2
            RetrievalPhase.L3_SEMANTIC: int(total_budget * 0.6),   # 60%给L3
        }
        self.phase_used = {phase: 0 for phase in RetrievalPhase}
    
    def allocate(self, phase: RetrievalPhase, cost: int) -> bool:
        """分配计算预算"""
        if self.phase_used[phase] + cost > self.phase_budgets[phase]:
            return False
        
        self.phase_used[phase] += cost
        self.used_budget += cost
        return True
    
    def get_remaining(self, phase: RetrievalPhase) -> int:
        """获取剩余预算"""
        return self.phase_budgets[phase] - self.phase_used[phase]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取预算使用统计"""
        return {
            "total_budget": self.total_budget,
            "used_budget": self.used_budget,
            "remaining_budget": self.total_budget - self.used_budget,
            "usage_rate": self.used_budget / self.total_budget if self.total_budget > 0 else 0,
            "phase_breakdown": {
                phase.value: {
                    "allocated": self.phase_budgets[phase],
                    "used": self.phase_used[phase],
                    "remaining": self.get_remaining(phase)
                }
                for phase in RetrievalPhase
            }
        }


class SemanticEncoder:
    """
    语义编码器
    
    将文本编码为语义向量，用于相似度计算
    基于简单的词频统计（可替换为embedding模型）
    """
    
    def __init__(self, dim: int = 128):
        self.dim = dim
        self.vocab = {}
        self.vocab_size = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 中文按字符，英文按单词
        import re
        
        # 提取中文
        chinese = re.findall(r'[\u4e00-\u9fa5]', text)
        # 提取英文单词
        english = re.findall(r'[a-zA-Z]+', text.lower())
        
        return chinese + english
    
    def _get_word_id(self, word: str) -> int:
        """获取词ID"""
        if word not in self.vocab:
            self.vocab[word] = self.vocab_size
            self.vocab_size += 1
        return self.vocab[word]
    
    def encode(self, text: str) -> np.ndarray:
        """
        编码文本为语义向量
        
        使用简单的词袋模型 + 哈希技巧
        """
        tokens = self._tokenize(text)
        
        # 使用哈希技巧创建固定维度向量
        vector = np.zeros(self.dim)
        
        for token in tokens:
            # 哈希到多个位置
            hash_val = int(hashlib.md5(token.encode()).hexdigest(), 16)
            idx = hash_val % self.dim
            vector[idx] += 1
        
        # L2归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的语义相似度"""
        vec1 = self.encode(text1)
        vec2 = self.encode(text2)
        
        # 余弦相似度
        return float(np.dot(vec1, vec2))


class IntelligentRetriever:
    """
    智能检索引擎
    
    Phase 2核心组件：
    - 计算预算管理
    - 分层检索策略
    - 语义相似度匹配
    - 智能结果排序
    """
    
    def __init__(
        self,
        compute_budget: int = 1_000_000,
        semantic_encoder: Optional[SemanticEncoder] = None
    ):
        self.budget_manager = ComputeBudgetManager(compute_budget)
        self.semantic_encoder = semantic_encoder or SemanticEncoder()
    
    def retrieve(
        self,
        query: str,
        l1_memories: List[Dict],
        l2_memories: Dict[str, Dict],
        l3_memories: Dict[str, Dict],
        top_k: int = 5,
        min_score: float = 0.3
    ) -> Tuple[List[RetrievalResult], Dict[str, Any]]:
        """
        智能检索主入口
        
        Args:
            query: 查询文本
            l1_memories: 工作记忆列表
            l2_memories: 短期记忆字典
            l3_memories: 长期记忆字典
            top_k: 返回结果数量
            min_score: 最小匹配分数
            
        Returns:
            (结果列表, 检索统计)
        """
        all_results = []
        
        # Phase 1: L1 快速检索
        l1_results = self._retrieve_l1(query, l1_memories, min_score)
        all_results.extend(l1_results)
        
        # 如果L1结果足够好，提前返回
        if len(all_results) >= top_k and self._avg_score(all_results) > 0.7:
            return self._finalize_results(all_results, top_k)
        
        # Phase 2: L2 结构检索
        remaining_slots = top_k - len(all_results)
        if remaining_slots > 0:
            l2_results = self._retrieve_l2(query, l2_memories, min_score, remaining_slots * 2)
            all_results.extend(l2_results)
        
        # Phase 3: L3 语义检索（如果预算允许）
        remaining_slots = top_k - len([r for r in all_results if r.score > min_score])
        if remaining_slots > 0 and self.budget_manager.get_remaining(RetrievalPhase.L3_SEMANTIC) > 1000:
            l3_results = self._retrieve_l3(query, l3_memories, min_score, remaining_slots * 3)
            all_results.extend(l3_results)
        
        return self._finalize_results(all_results, top_k)
    
    def _retrieve_l1(
        self,
        query: str,
        memories: List[Dict],
        min_score: float
    ) -> List[RetrievalResult]:
        """
        L1工作记忆检索 - 最快
        
        策略：关键词匹配 + 最近访问
        成本：每个记忆 ~10单位
        """
        results = []
        query_words = set(self._tokenize(query.lower()))
        
        for memory in memories:
            # 检查预算
            if not self.budget_manager.allocate(RetrievalPhase.L1_FAST, 10):
                break
            
            # 快速关键词匹配
            content_words = set(self._tokenize(memory.get("content", "").lower()))
            
            if not query_words or not content_words:
                continue
            
            # Jaccard相似度
            intersection = len(query_words & content_words)
            union = len(query_words | content_words)
            score = intersection / union if union > 0 else 0
            
            # 时间衰减加成（最近访问的记忆获得加成）
            time_bonus = self._compute_time_bonus(memory)
            final_score = min(1.0, score * 0.8 + time_bonus * 0.2)
            
            if final_score >= min_score:
                results.append(RetrievalResult(
                    memory=memory,
                    score=final_score,
                    phase=RetrievalPhase.L1_FAST,
                    match_details={
                        "keyword_match": score,
                        "time_bonus": time_bonus,
                        "common_words": list(query_words & content_words)
                    }
                ))
        
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def _retrieve_l2(
        self,
        query: str,
        memories: Dict[str, Dict],
        min_score: float,
        max_results: int
    ) -> List[RetrievalResult]:
        """
        L2短期记忆检索 - 结构匹配
        
        策略：实体匹配 + 主题匹配 + 模板匹配
        成本：每个记忆 ~50单位
        """
        results = []
        
        # 提取查询特征
        query_entities = self._extract_entities(query)
        query_topics = self._extract_topics(query)
        
        for memory_id, memory in memories.items():
            # 检查预算
            if not self.budget_manager.allocate(RetrievalPhase.L2_STRUCTURE, 50):
                break
            
            if len(results) >= max_results:
                break
            
            structure = memory.get("structure", {})
            scores = []
            match_details = {}
            
            # 1. 实体匹配 (0-0.4)
            memory_entities = [e.get("text", "") for e in structure.get("entities", [])]
            entity_overlap = len(set(query_entities) & set(memory_entities))
            if query_entities:
                entity_score = entity_overlap / len(query_entities) * 0.4
                scores.append(entity_score)
                match_details["entity_match"] = entity_score
            
            # 2. 主题匹配 (0-0.3)
            memory_topics = structure.get("topics", [])
            topic_overlap = len(set(query_topics) & set(memory_topics))
            if query_topics:
                topic_score = topic_overlap / len(query_topics) * 0.3
                scores.append(topic_score)
                match_details["topic_match"] = topic_score
            
            # 3. 模板匹配 (0-0.2)
            query_templates = self._identify_templates(query)
            memory_templates = structure.get("templates", [])
            template_overlap = len(set(query_templates) & set(memory_templates))
            if query_templates:
                template_score = template_overlap / len(query_templates) * 0.2
                scores.append(template_score)
                match_details["template_match"] = template_score
            
            # 4. 内容相似度 (0-0.1)
            content_sim = SequenceMatcher(
                None, query.lower(), memory.get("content", "").lower()
            ).ratio()
            scores.append(content_sim * 0.1)
            match_details["content_similarity"] = content_sim
            
            # 计算最终分数
            final_score = sum(scores) if scores else 0
            
            # Epiplexity加成（高Epiplexity记忆获得加成）
            epiplexity_bonus = memory.get("epiplexity_score", 0) * 0.1
            final_score = min(1.0, final_score + epiplexity_bonus)
            
            if final_score >= min_score:
                match_details["epiplexity_bonus"] = epiplexity_bonus
                results.append(RetrievalResult(
                    memory=memory,
                    score=final_score,
                    phase=RetrievalPhase.L2_STRUCTURE,
                    match_details=match_details
                ))
        
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def _retrieve_l3(
        self,
        query: str,
        memories: Dict[str, Dict],
        min_score: float,
        max_results: int
    ) -> List[RetrievalResult]:
        """
        L3长期记忆检索 - 语义匹配
        
        策略：语义向量相似度 + 抽象结构匹配
        成本：每个记忆 ~100单位
        只检索高Epiplexity记忆
        """
        results = []
        
        # 只检索高Epiplexity记忆（>0.6）
        high_value_memories = [
            (mid, mem) for mid, mem in memories.items()
            if mem.get("epiplexity_score", 0) > 0.6
        ]
        
        # 按访问频率排序（优先检索常用记忆）
        high_value_memories.sort(
            key=lambda x: x[1].get("access_count", 0),
            reverse=True
        )
        
        for memory_id, memory in high_value_memories:
            # 检查预算
            if not self.budget_manager.allocate(RetrievalPhase.L3_SEMANTIC, 100):
                break
            
            if len(results) >= max_results:
                break
            
            # 语义相似度计算
            semantic_sim = self.semantic_encoder.similarity(
                query, memory.get("content", "")
            )
            
            # 结构相似度
            structure_sim = self._compute_structure_similarity(
                query, memory.get("structure", {})
            )
            
            # 综合分数
            final_score = semantic_sim * 0.6 + structure_sim * 0.4
            
            # 访问频率加成
            access_bonus = min(0.1, memory.get("access_count", 0) * 0.01)
            final_score = min(1.0, final_score + access_bonus)
            
            if final_score >= min_score:
                results.append(RetrievalResult(
                    memory=memory,
                    score=final_score,
                    phase=RetrievalPhase.L3_SEMANTIC,
                    match_details={
                        "semantic_similarity": semantic_sim,
                        "structure_similarity": structure_sim,
                        "access_bonus": access_bonus
                    }
                ))
        
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def _finalize_results(
        self,
        results: List[RetrievalResult],
        top_k: int
    ) -> Tuple[List[RetrievalResult], Dict[str, Any]]:
        """整理最终结果"""
        # 去重（按memory ID）
        seen_ids = set()
        unique_results = []
        
        for result in results:
            mem_id = result.memory.get("id")
            if mem_id not in seen_ids:
                seen_ids.add(mem_id)
                unique_results.append(result)
        
        # 排序并截取top_k
        unique_results.sort(key=lambda x: x.score, reverse=True)
        final_results = unique_results[:top_k]
        
        # 生成统计
        stats = {
            "total_candidates": len(results),
            "unique_results": len(unique_results),
            "returned_results": len(final_results),
            "avg_score": np.mean([r.score for r in final_results]) if final_results else 0,
            "phase_distribution": {
                phase.value: len([r for r in final_results if r.phase == phase])
                for phase in RetrievalPhase
            },
            "budget_stats": self.budget_manager.get_stats()
        }
        
        return final_results, stats
    
    # Helper methods
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        import re
        chinese = re.findall(r'[\u4e00-\u9fa5]', text)
        english = re.findall(r'[a-zA-Z]+', text)
        return chinese + english
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取实体"""
        import re
        # 简单规则
        entities = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        entities += re.findall(r'[A-Z][a-z]+', text)
        return entities
    
    def _extract_topics(self, text: str) -> List[str]:
        """提取主题"""
        topic_keywords = {
            "AGI": ["agi", "人工智能", "认知"],
            "MEMORY": ["记忆", "存储"],
            "CODE": ["代码", "编程"],
        }
        
        topics = []
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def _identify_templates(self, text: str) -> List[str]:
        """识别模板"""
        templates = []
        if "?" in text or "？" in text:
            templates.append("QUESTION")
        if any(w in text for w in ["请", "能不能"]):
            templates.append("REQUEST")
        return templates
    
    def _compute_time_bonus(self, memory: Dict) -> float:
        """计算时间加成"""
        from datetime import datetime
        
        last_accessed = memory.get("last_accessed")
        if not last_accessed:
            return 0
        
        try:
            last_time = datetime.fromisoformat(last_accessed)
            now = datetime.now()
            hours_ago = (now - last_time).total_seconds() / 3600
            
            # 最近访问的记忆获得更高加成
            if hours_ago < 1:
                return 0.3
            elif hours_ago < 24:
                return 0.2
            elif hours_ago < 168:  # 一周
                return 0.1
            else:
                return 0
        except:
            return 0
    
    def _compute_structure_similarity(self, query: str, structure: Dict) -> float:
        """计算结构相似度"""
        scores = []
        
        # 实体匹配
        query_entities = self._extract_entities(query)
        memory_entities = [e.get("text", "") for e in structure.get("entities", [])]
        
        if query_entities and memory_entities:
            overlap = len(set(query_entities) & set(memory_entities))
            scores.append(overlap / max(len(query_entities), len(memory_entities)))
        
        return sum(scores) / len(scores) if scores else 0
    
    def _avg_score(self, results: List[RetrievalResult]) -> float:
        """计算平均分数"""
        if not results:
            return 0
        return sum(r.score for r in results) / len(results)
