"""
对话结构提取器

专门用于从对话中提取Epiplexity结构
基于arXiv:2601.03220理论
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DialogueTurn:
    """对话轮次"""
    speaker: str
    content: str
    timestamp: Optional[str] = None
    turn_id: int = 0


@dataclass
class DialogueStructure:
    """对话结构"""
    turns: List[DialogueTurn]
    topics: List[str]
    entities: List[Dict]
    relations: List[Dict]
    intents: List[str]
    epiplexity_score: float
    

class DialogueStructureExtractor:
    """
    对话结构提取器
    
    从对话中提取高Epiplexity的结构信息：
    - 主题识别
    - 意图分类
    - 实体关系
    - 对话流程
    """
    
    def __init__(self):
        # 意图模式库
        self.intent_patterns = {
            "QUESTION": [r"什么|怎么|为什么|如何|哪里|谁|多少|吗\?|？"],
            "REQUEST": [r"请|能不能|可以|能否|帮忙|需要|想要"],
            "INFORM": [r"是|有|在|做了|完成了|实现了"],
            "CONFIRM": [r"好的|明白|了解|确认|同意|是的|对"],
            "REJECT": [r"不|不行|不对|错误|问题|bug"],
            "SUGGEST": [r"建议|应该|可以|试试|考虑"],
            "COMMAND": [r"立即|马上|必须|执行|开始|停止"],
        }
        
        # 主题关键词库
        self.topic_keywords = {
            "AGI": ["agi", "通用人工智能", "递归", "认知", "意识"],
            "MEMORY": ["记忆", "存储", "回忆", "遗忘", "记住"],
            "CODE": ["代码", "编程", "实现", "函数", "类", "模块"],
            "RESEARCH": ["研究", "论文", "理论", "实验", "分析"],
            "SYSTEM": ["系统", "架构", "设计", "模块", "接口"],
            "DATA": ["数据", "信息", "知识", "图谱", "记录"],
        }
    
    def extract(self, dialogue_text: str) -> DialogueStructure:
        """
        从对话文本提取结构
        
        Args:
            dialogue_text: 原始对话文本
            
        Returns:
            DialogueStructure: 对话结构
        """
        # 解析对话轮次
        turns = self._parse_turns(dialogue_text)
        
        # 提取主题
        topics = self._extract_topics(dialogue_text)
        
        # 提取实体
        entities = self._extract_entities(dialogue_text)
        
        # 提取关系
        relations = self._extract_relations(turns, entities)
        
        # 识别意图
        intents = self._identify_intents(dialogue_text)
        
        # 计算Epiplexity评分
        epiplexity = self._compute_dialogue_epiplexity(
            turns, topics, entities, relations, intents
        )
        
        return DialogueStructure(
            turns=turns,
            topics=topics,
            entities=entities,
            relations=relations,
            intents=intents,
            epiplexity_score=epiplexity
        )
    
    def _parse_turns(self, text: str) -> List[DialogueTurn]:
        """解析对话轮次"""
        turns = []
        
        # 匹配 "陈学东: xxx" 或 "OpenClaw-Rft: xxx" 格式
        pattern = r'([\u4e00-\u9fa5\w\-]+)[\s]*[:：][\s]*(.*?)(?=\n[\u4e00-\u9fa5\w\-]+[\s]*[:：]|\Z)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for i, (speaker, content) in enumerate(matches):
            turns.append(DialogueTurn(
                speaker=speaker.strip(),
                content=content.strip(),
                turn_id=i
            ))
        
        return turns
    
    def _extract_topics(self, text: str) -> List[str]:
        """提取对话主题"""
        topics = []
        text_lower = text.lower()
        
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    topics.append(topic)
                    break
        
        return list(set(topics))
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """提取命名实体"""
        entities = []
        
        # 人名提取
        person_patterns = [
            (r"([\u4e00-\u9fa5]{2,4})(?:博士|教授|先生|女士|老师)", "PERSON"),
            (r"(OpenClaw-[\w]+)", "AI_AGENT"),
            (r"([A-Z][a-z]+[\s-]?[A-Z][a-z]*)", "PERSON"),
        ]
        
        for pattern, entity_type in person_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                entities.append({
                    "text": match,
                    "type": entity_type,
                    "confidence": 0.85
                })
        
        # 技术实体
        tech_patterns = [
            (r"(EMS|RCC-E|AGI|LLM|GPT|Epiplexity)", "TECH"),
            (r"([\w-]+\.py)", "CODE_FILE"),
            (r"([\w-]+\.md)", "DOC_FILE"),
            (r"(arXiv:\d+\.\d+)", "PAPER"),
        ]
        
        for pattern, entity_type in tech_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                entities.append({
                    "text": match,
                    "type": entity_type,
                    "confidence": 0.9
                })
        
        # 时间实体
        time_patterns = [
            (r"(\d{4}-\d{2}-\d{2})", "DATE"),
            (r"(\d{1,2}:\d{2})", "TIME"),
            (r"(明天|今天|昨天|下周|上周|现在)", "RELATIVE_TIME"),
        ]
        
        for pattern, entity_type in time_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                entities.append({
                    "text": match,
                    "type": entity_type,
                    "confidence": 0.95
                })
        
        # 去重
        seen = set()
        unique_entities = []
        for e in entities:
            key = (e["text"], e["type"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(e)
        
        return unique_entities
    
    def _extract_relations(
        self, 
        turns: List[DialogueTurn], 
        entities: List[Dict]
    ) -> List[Dict]:
        """提取实体间关系"""
        relations = []
        
        # 共现关系
        entity_texts = [e["text"] for e in entities]
        
        for i, turn in enumerate(turns):
            turn_entities = [e for e in entity_texts if e in turn.content]
            
            # 同一句中的实体建立关系
            for j, e1 in enumerate(turn_entities):
                for e2 in turn_entities[j+1:]:
                    relations.append({
                        "source": e1,
                        "target": e2,
                        "type": "CO_OCCUR",
                        "context": turn.content[:50],
                        "confidence": 0.7
                    })
        
        # 动作关系
        action_patterns = [
            (r"(\w+)\s*(?:说|表示|认为|提出|建议)", "EXPRESS"),
            (r"(\w+)\s*(?:做|完成|实现|构建|创建)", "CREATE"),
            (r"(\w+)\s*(?:使用|采用|基于|利用)", "USE"),
        ]
        
        for turn in turns:
            for pattern, rel_type in action_patterns:
                matches = re.findall(pattern, turn.content)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    # 找到最近的实体
                    for entity in entity_texts:
                        if entity in turn.content:
                            relations.append({
                                "source": match,
                                "target": entity,
                                "type": rel_type,
                                "context": turn.content[:50],
                                "confidence": 0.75
                            })
                            break
        
        return relations
    
    def _identify_intents(self, text: str) -> List[str]:
        """识别对话意图"""
        intents = []
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    intents.append(intent)
                    break
        
        return list(set(intents))
    
    def _compute_dialogue_epiplexity(
        self,
        turns: List[DialogueTurn],
        topics: List[str],
        entities: List[Dict],
        relations: List[Dict],
        intents: List[str]
    ) -> float:
        """
        计算对话的Epiplexity评分
        
        高Epiplexity对话特征：
        - 多轮次交互
        - 明确的主题
        - 丰富的实体和关系
        - 清晰的意图
        """
        scores = []
        
        # 轮次复杂度 (0-0.2)
        turn_score = min(0.2, len(turns) * 0.05)
        scores.append(turn_score)
        
        # 主题明确度 (0-0.2)
        topic_score = min(0.2, len(topics) * 0.1)
        scores.append(topic_score)
        
        # 实体丰富度 (0-0.2)
        entity_score = min(0.2, len(entities) * 0.05)
        scores.append(entity_score)
        
        # 关系复杂度 (0-0.2)
        relation_score = min(0.2, len(relations) * 0.03)
        scores.append(relation_score)
        
        # 意图清晰度 (0-0.2)
        intent_score = min(0.2, len(intents) * 0.1)
        scores.append(intent_score)
        
        return sum(scores)
    
    def encode_for_memory(
        self, 
        dialogue_text: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        将对话编码为记忆格式
        
        Returns:
            记忆节点格式
        """
        structure = self.extract(dialogue_text)
        
        return {
            "type": "dialogue",
            "content": dialogue_text,
            "structure": {
                "turns": [
                    {
                        "speaker": t.speaker,
                        "content": t.content[:200],  # 截断
                        "turn_id": t.turn_id
                    }
                    for t in structure.turns
                ],
                "topics": structure.topics,
                "entities": structure.entities,
                "relations": structure.relations,
                "intents": structure.intents,
            },
            "epiplexity_score": structure.epiplexity_score,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
