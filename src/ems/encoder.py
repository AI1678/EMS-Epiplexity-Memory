"""
Epiplexity编码器

将原始内容编码为结构程序 + 残差熵
"""

import re
from typing import Dict, List, Optional, Any


class StructureEncoder:
    """
    结构编码器
    
    提取内容中的可复用模式（结构程序），
    并计算残差熵（不可压缩部分）。
    """
    
    def __init__(self, compute_budget: int):
        self.compute_budget = compute_budget
        
        # 预定义的模式模板
        self.patterns = {
            "datetime": r"\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}",
            "email": r"[\w.-]+@[\w.-]+\.\w+",
            "url": r"https?://[^\s]+",
            "mention": r"@\w+",
            "hashtag": r"#\w+",
        }
    
    def encode(self, content: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Epiplexity编码
        
        Returns:
            {
                "structure": 结构程序（可复用模式）,
                "residual": 残差熵（不可压缩部分）,
                "epiplexity_score": Epiplexity评分 0-1
            }
        """
        # 提取结构化信息
        structure = self._extract_structure(content, context)
        
        # 计算残差（去除结构后的内容）
        residual = self._compute_residual(content, structure)
        
        # 计算Epiplexity评分
        epiplexity_score = self._compute_epiplexity(content, structure, residual)
        
        return {
            "structure": structure,
            "residual": residual,
            "epiplexity_score": epiplexity_score
        }
    
    def _extract_structure(
        self, 
        content: str, 
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        提取结构程序
        
        识别内容中的模式、实体、关系
        """
        structure = {
            "templates": [],
            "entities": [],
            "relations": [],
            "patterns": []
        }
        
        # 提取实体
        structure["entities"] = self._extract_entities(content)
        
        # 提取关系
        structure["relations"] = self._extract_relations(content, structure["entities"])
        
        # 识别模板
        structure["templates"] = self._identify_templates(content)
        
        # 匹配预定义模式
        for pattern_name, pattern_regex in self.patterns.items():
            matches = re.findall(pattern_regex, content)
            if matches:
                structure["patterns"].append({
                    "type": pattern_name,
                    "matches": matches
                })
        
        # 添加上下文信息
        if context:
            structure["context_keys"] = list(context.keys())
        
        return structure
    
    def _extract_entities(self, content: str) -> List[Dict]:
        """提取命名实体"""
        entities = []
        
        # 简单规则提取（可扩展为NER模型）
        # 人名
        name_patterns = [
            r"([\u4e00-\u9fa5]{2,4})(?:博士|教授|先生|女士)",  # 中文称谓
            r"(?:Mr\.?|Mrs\.?|Dr\.?|Prof\.?)\s+([A-Z][a-z]+)",  # 英文称谓
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                entities.append({
                    "text": match,
                    "type": "PERSON",
                    "confidence": 0.8
                })
        
        # 时间
        time_patterns = [
            r"(\d{1,2}):(\d{2})",
            r"(明天|今天|昨天|下周|上周)",
            r"(\d{4})年(\d{1,2})月(\d{1,2})日"
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                entities.append({
                    "text": str(match),
                    "type": "TIME",
                    "confidence": 0.9
                })
        
        return entities
    
    def _extract_relations(
        self, 
        content: str, 
        entities: List[Dict]
    ) -> List[Dict]:
        """提取实体间关系"""
        relations = []
        
        # 简单的共现关系
        if len(entities) >= 2:
            for i, e1 in enumerate(entities):
                for e2 in entities[i+1:]:
                    relations.append({
                        "source": e1["text"],
                        "target": e2["text"],
                        "type": "CO_OCCUR",
                        "confidence": 0.6
                    })
        
        # 动作关系
        action_patterns = [
            r"(\w+)\s+(?:说|表示|认为|提出)",
            r"(\w+)\s+(?:will|going to)\s+(\w+)"
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                relations.append({
                    "source": match[0] if isinstance(match, tuple) else match,
                    "target": "action",
                    "type": "ACTION",
                    "confidence": 0.7
                })
        
        return relations
    
    def _identify_templates(self, content: str) -> List[str]:
        """识别内容模板"""
        templates = []
        
        # 常见对话模板
        if "?" in content or "？" in content:
            templates.append("QUESTION")
        
        if content.startswith(("请", "能不能", "可以", "能否")):
            templates.append("REQUEST")
        
        if any(word in content for word in ["谢谢", "感谢", "thank"]):
            templates.append("GRATITUDE")
        
        if any(word in content for word in ["问题", "错误", "bug", "issue"]):
            templates.append("PROBLEM_REPORT")
        
        return templates
    
    def _compute_residual(
        self, 
        content: str, 
        structure: Dict
    ) -> Dict[str, Any]:
        """
        计算残差熵
        
        去除结构后的不可压缩信息
        """
        residual_text = content
        
        # 移除已识别的实体
        for entity in structure.get("entities", []):
            residual_text = residual_text.replace(entity["text"], "[ENTITY]")
        
        # 移除已识别的模式
        for pattern in structure.get("patterns", []):
            for match in pattern.get("matches", []):
                residual_text = residual_text.replace(match, f"[{pattern['type'].upper()}]")
        
        # 计算残差长度
        residual_length = len(residual_text)
        original_length = len(content)
        
        # 压缩率
        compression_ratio = 1 - (residual_length / original_length) if original_length > 0 else 0
        
        return {
            "text": residual_text,
            "length": residual_length,
            "original_length": original_length,
            "compression_ratio": compression_ratio
        }
    
    def _compute_epiplexity(
        self, 
        content: str, 
        structure: Dict, 
        residual: Dict
    ) -> float:
        """
        计算Epiplexity评分
        
        评分标准:
        - 高结构复杂度 + 低残差 = 高Epiplexity
        - 可复用模式多 = 高Epiplexity
        - 实体和关系丰富 = 高Epiplexity
        """
        scores = []
        
        # 结构丰富度 (0-0.4)
        entity_count = len(structure.get("entities", []))
        relation_count = len(structure.get("relations", []))
        template_count = len(structure.get("templates", []))
        
        structure_score = min(0.4, (entity_count * 0.1 + relation_count * 0.05 + template_count * 0.1))
        scores.append(structure_score)
        
        # 压缩率 (0-0.3)
        compression_score = residual.get("compression_ratio", 0) * 0.3
        scores.append(compression_score)
        
        # 内容长度因子 (0-0.2)
        length_score = min(0.2, len(content) / 500 * 0.2)
        scores.append(length_score)
        
        # 模式匹配度 (0-0.1)
        pattern_score = len(structure.get("patterns", [])) * 0.025
        scores.append(min(0.1, pattern_score))
        
        return sum(scores)
