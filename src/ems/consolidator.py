"""
记忆巩固器

实现睡眠时的记忆整合
"""

from typing import Dict, List, Any
from collections import defaultdict


class MemoryConsolidator:
    """
    记忆巩固器
    
    将短期记忆整合到长期记忆，
    提取跨事件的共同结构。
    """
    
    def __init__(self):
        self.pattern_threshold = 2  # 最小出现次数才算模式
    
    def consolidate(
        self,
        l2_memories: Dict[str, Dict],
        l3_memories: Dict[str, Dict]
    ):
        """
        执行记忆巩固
        
        1. 提取跨记忆共同结构
        2. 合并相似记忆
        3. 更新长期记忆
        """
        if not l2_memories:
            return
        
        # 提取共同模式
        common_patterns = self._extract_common_patterns(l2_memories)
        
        # 聚类相似记忆
        clusters = self._cluster_memories(l2_memories)
        
        # 为每个聚类创建抽象记忆
        for cluster_id, memories in clusters.items():
            if len(memories) >= self.pattern_threshold:
                abstract_memory = self._create_abstract_memory(memories)
                
                # 添加到L3
                memory_id = f"abstract_{cluster_id}"
                l3_memories[memory_id] = abstract_memory
        
        # 更新实体关系图
        self._update_knowledge_graph(l2_memories, l3_memories)
    
    def _extract_common_patterns(
        self, 
        memories: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """提取跨记忆的共同模式"""
        patterns = {
            "entities": defaultdict(int),
            "relations": defaultdict(int),
            "templates": defaultdict(int),
            "contexts": defaultdict(int)
        }
        
        for memory in memories.values():
            structure = memory.get("structure", {})
            
            # 统计实体
            for entity in structure.get("entities", []):
                key = (entity["type"], entity["text"])
                patterns["entities"][key] += 1
            
            # 统计关系
            for relation in structure.get("relations", []):
                key = (relation["type"], relation["source"], relation["target"])
                patterns["relations"][key] += 1
            
            # 统计模板
            for template in structure.get("templates", []):
                patterns["templates"][template] += 1
            
            # 统计上下文
            for key in structure.get("context_keys", []):
                patterns["contexts"][key] += 1
        
        # 筛选高频模式
        common = {}
        for category, counts in patterns.items():
            common[category] = {
                k: v for k, v in counts.items() 
                if v >= self.pattern_threshold
            }
        
        return common
    
    def _cluster_memories(
        self, 
        memories: Dict[str, Dict]
    ) -> Dict[str, List[Dict]]:
        """聚类相似记忆"""
        clusters = defaultdict(list)
        assigned = set()
        
        for mem_id, memory in memories.items():
            if mem_id in assigned:
                continue
            
            # 找到最相似的聚类
            best_cluster = None
            best_similarity = 0.5  # 阈值
            
            for cluster_id, cluster_mems in clusters.items():
                for cluster_mem in cluster_mems:
                    similarity = self._compute_similarity(memory, cluster_mem)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_cluster = cluster_id
            
            if best_cluster:
                clusters[best_cluster].append(memory)
                assigned.add(mem_id)
            else:
                # 创建新聚类
                new_cluster_id = f"cluster_{len(clusters)}"
                clusters[new_cluster_id].append(memory)
                assigned.add(mem_id)
        
        return clusters
    
    def _compute_similarity(self, mem1: Dict, mem2: Dict) -> float:
        """计算两个记忆的相似度"""
        scores = []
        
        # 结构相似度
        struct1 = mem1.get("structure", {})
        struct2 = mem2.get("structure", {})
        
        # 实体重叠
        entities1 = {e["text"] for e in struct1.get("entities", [])}
        entities2 = {e["text"] for e in struct2.get("entities", [])}
        
        if entities1 and entities2:
            overlap = len(entities1 & entities2)
            union = len(entities1 | entities2)
            scores.append(overlap / union if union > 0 else 0)
        
        # 模板相似度
        templates1 = set(struct1.get("templates", []))
        templates2 = set(struct2.get("templates", []))
        
        if templates1 and templates2:
            overlap = len(templates1 & templates2)
            union = len(templates1 | templates2)
            scores.append(overlap / union if union > 0 else 0)
        
        # 上下文相似度
        context1 = set(struct1.get("context_keys", []))
        context2 = set(struct2.get("context_keys", []))
        
        if context1 and context2:
            overlap = len(context1 & context2)
            union = len(context1 | context2)
            scores.append(overlap / union if union > 0 else 0)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _create_abstract_memory(self, memories: List[Dict]) -> Dict:
        """从聚类创建抽象记忆"""
        from datetime import datetime
        
        # 提取共同特征
        common_entities = self._get_common_entities(memories)
        common_templates = self._get_common_templates(memories)
        
        # 生成摘要
        summary = self._generate_summary(memories)
        
        return {
            "id": f"abstract_{datetime.now().timestamp()}",
            "type": "abstract",
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "source_count": len(memories),
            "structure": {
                "entities": common_entities,
                "templates": common_templates,
                "abstracted_from": [m["id"] for m in memories]
            },
            "epiplexity_score": 0.9,  # 抽象记忆具有高Epiplexity
            "access_count": 0,
            "layer": "l3"
        }
    
    def _get_common_entities(self, memories: List[Dict]) -> List[Dict]:
        """提取共同实体"""
        entity_counts = defaultdict(int)
        
        for memory in memories:
            for entity in memory.get("structure", {}).get("entities", []):
                key = (entity["type"], entity["text"])
                entity_counts[key] += 1
        
        # 返回出现次数超过一半的记忆中的实体
        threshold = len(memories) / 2
        common = []
        for (etype, etext), count in entity_counts.items():
            if count >= threshold:
                common.append({
                    "type": etype,
                    "text": etext,
                    "frequency": count / len(memories)
                })
        
        return common
    
    def _get_common_templates(self, memories: List[Dict]) -> List[str]:
        """提取共同模板"""
        template_counts = defaultdict(int)
        
        for memory in memories:
            for template in memory.get("structure", {}).get("templates", []):
                template_counts[template] += 1
        
        threshold = len(memories) / 2
        return [t for t, c in template_counts.items() if c >= threshold]
    
    def _generate_summary(self, memories: List[Dict]) -> str:
        """生成聚类摘要"""
        # 简单摘要：提取关键词
        all_content = " ".join([m["content"] for m in memories])
        
        # 返回前100字符作为摘要
        return all_content[:100] + "..." if len(all_content) > 100 else all_content
    
    def _update_knowledge_graph(
        self,
        l2_memories: Dict[str, Dict],
        l3_memories: Dict[str, Dict]
    ):
        """更新知识图谱"""
        # 构建实体关系图
        graph = {
            "entities": set(),
            "relations": []
        }
        
        for memory in list(l2_memories.values()) + list(l3_memories.values()):
            structure = memory.get("structure", {})
            
            for entity in structure.get("entities", []):
                graph["entities"].add((entity["type"], entity["text"]))
            
            for relation in structure.get("relations", []):
                graph["relations"].append(relation)
        
        # 这里可以将graph持久化到知识图谱系统
        # 与现有的knowledge-graph-memory.py集成
