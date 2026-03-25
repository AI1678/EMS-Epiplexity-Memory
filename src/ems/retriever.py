"""
分层检索器

实现计算预算内的分层记忆检索
"""

from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher


class HierarchicalRetriever:
    """
    分层记忆检索器
    
    在计算预算内，按L1→L2→L3的顺序检索记忆
    """
    
    def __init__(self, compute_budget: int):
        self.compute_budget = compute_budget
        self.budget_used = 0
    
    def retrieve(
        self,
        query: str,
        l1_memories: List[Dict],
        l2_memories: Dict[str, Dict],
        l3_memories: Dict[str, Dict],
        top_k: int = 5,
        compute_budget: Optional[int] = None
    ) -> List[Dict]:
        """
        分层检索
        
        策略:
        1. 快速过滤: 关键词匹配 (低计算)
        2. 结构匹配: 实体/关系匹配 (中等计算)
        3. 语义匹配: 相似度计算 (高计算)
        """
        budget = compute_budget or self.compute_budget
        self.budget_used = 0
        
        results = []
        
        # Phase 1: L1工作记忆检索 (最快)
        l1_results = self._search_l1(query, l1_memories)
        results.extend(l1_results)
        
        if len(results) >= top_k:
            return results[:top_k]
        
        # Phase 2: L2短期记忆检索
        remaining_budget = budget - self.budget_used
        l2_results = self._search_l2(query, l2_memories, remaining_budget)
        results.extend(l2_results)
        
        if len(results) >= top_k:
            return results[:top_k]
        
        # Phase 3: L3长期记忆检索 (最慢，仅对高价值记忆)
        remaining_budget = budget - self.budget_used
        if remaining_budget > budget * 0.3:  # 保留30%预算给L3
            l3_results = self._search_l3(query, l3_memories, remaining_budget)
            results.extend(l3_results)
        
        # 排序并返回top_k
        results = self._rank_results(results, query)
        return results[:top_k]
    
    def _search_l1(self, query: str, memories: List[Dict]) -> List[Dict]:
        """搜索L1工作记忆 (O(n))"""
        results = []
        
        for memory in memories:
            score = self._quick_match(query, memory["content"])
            if score > 0.3:
                memory["match_score"] = score
                results.append(memory)
            
            self.budget_used += 10  # 低成本操作
        
        return sorted(results, key=lambda x: x["match_score"], reverse=True)
    
    def _search_l2(
        self, 
        query: str, 
        memories: Dict[str, Dict],
        budget: int
    ) -> List[Dict]:
        """搜索L2短期记忆 (结构匹配)"""
        results = []
        
        for memory_id, memory in memories.items():
            if self.budget_used >= budget:
                break
            
            # 结构匹配
            score = self._structure_match(query, memory)
            
            if score > 0.4:
                memory["match_score"] = score
                results.append(memory)
            
            self.budget_used += 50  # 中等成本
        
        return sorted(results, key=lambda x: x["match_score"], reverse=True)
    
    def _search_l3(
        self, 
        query: str, 
        memories: Dict[str, Dict],
        budget: int
    ) -> List[Dict]:
        """搜索L3长期记忆 (仅高Epiplexity)"""
        results = []
        
        # 只检索高Epiplexity的记忆
        high_value_memories = [
            m for m in memories.values() 
            if m.get("epiplexity_score", 0) > 0.6
        ]
        
        for memory in high_value_memories:
            if self.budget_used >= budget:
                break
            
            # 深度语义匹配
            score = self._semantic_match(query, memory)
            
            if score > 0.5:
                memory["match_score"] = score
                results.append(memory)
            
            self.budget_used += 100  # 高成本操作
        
        return sorted(results, key=lambda x: x["match_score"], reverse=True)
    
    def _quick_match(self, query: str, content: str) -> float:
        """快速匹配 (关键词)"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words & content_words)
        return overlap / len(query_words)
    
    def _structure_match(self, query: str, memory: Dict) -> float:
        """结构匹配 (实体/关系)"""
        scores = []
        
        # 提取查询中的关键词
        query_entities = self._extract_entities(query)
        
        # 匹配记忆结构中的实体
        memory_entities = memory.get("structure", {}).get("entities", [])
        memory_entity_texts = [e["text"] for e in memory_entities]
        
        for entity in query_entities:
            if entity in memory_entity_texts:
                scores.append(0.8)
        
        # 匹配模板
        query_templates = self._identify_templates(query)
        memory_templates = memory.get("structure", {}).get("templates", [])
        
        for template in query_templates:
            if template in memory_templates:
                scores.append(0.6)
        
        # 内容相似度
        content_score = SequenceMatcher(None, query.lower(), memory["content"].lower()).ratio()
        scores.append(content_score * 0.4)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _semantic_match(self, query: str, memory: Dict) -> float:
        """语义匹配 (深度相似度)"""
        # 这里可以集成embedding模型
        # 目前使用改进的字符串匹配
        
        content = memory["content"]
        
        # 多粒度匹配
        scores = []
        
        # 字符级
        char_score = SequenceMatcher(None, query, content).ratio()
        scores.append(char_score * 0.3)
        
        # 词级
        query_words = query.split()
        content_words = content.split()
        
        if query_words and content_words:
            word_score = SequenceMatcher(None, query_words, content_words).ratio()
            scores.append(word_score * 0.4)
        
        # 结构匹配加成
        structure_score = self._structure_match(query, memory)
        scores.append(structure_score * 0.3)
        
        return sum(scores)
    
    def _rank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """结果排序 (综合评分)"""
        for result in results:
            # 基础匹配分
            base_score = result.get("match_score", 0)
            
            # Epiplexity加成
            epiplexity = result.get("epiplexity_score", 0)
            
            # 访问频率加成
            access_bonus = min(0.1, result.get("access_count", 0) * 0.01)
            
            # 重要性加成
            importance = result.get("importance", 1.0) * 0.1
            
            # 综合评分
            result["final_score"] = base_score * 0.5 + epiplexity * 0.3 + access_bonus + importance
        
        return sorted(results, key=lambda x: x["final_score"], reverse=True)
    
    def _extract_entities(self, text: str) -> List[str]:
        """简单实体提取"""
        import re
        
        entities = []
        
        # 中文人名
        matches = re.findall(r"[\u4e00-\u9fa5]{2,4}", text)
        entities.extend(matches)
        
        # 英文单词
        matches = re.findall(r"[A-Z][a-z]+", text)
        entities.extend(matches)
        
        return entities
    
    def _identify_templates(self, text: str) -> List[str]:
        """识别模板"""
        templates = []
        
        if "?" in text or "？" in text:
            templates.append("QUESTION")
        
        if any(word in text for word in ["请", "能不能", "可以"]):
            templates.append("REQUEST")
        
        return templates
