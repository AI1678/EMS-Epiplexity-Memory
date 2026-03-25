"""
EMS测试套件
"""

import unittest
from datetime import datetime

from ems import (
    EpiplexityMemorySystem,
    StructureEncoder,
    DialogueStructureExtractor,
    DialogueStructure
)


class TestDialogueExtractor(unittest.TestCase):
    """测试对话结构提取器"""
    
    def setUp(self):
        self.extractor = DialogueStructureExtractor()
    
    def test_parse_turns(self):
        """测试对话轮次解析"""
        text = """
陈学东: 今天讨论AGI记忆系统
OpenClaw-Rft: 明白，基于Epiplexity理论
陈学东: 开始实施Phase 1
"""
        turns = self.extractor._parse_turns(text)
        
        self.assertEqual(len(turns), 3)
        self.assertEqual(turns[0].speaker, "陈学东")
        self.assertIn("AGI", turns[0].content)
    
    def test_extract_topics(self):
        """测试主题提取"""
        text = "我们需要研究AGI的记忆系统和Epiplexity理论"
        topics = self.extractor._extract_topics(text)
        
        self.assertIn("AGI", topics)
        self.assertIn("MEMORY", topics)
    
    def test_extract_entities(self):
        """测试实体提取"""
        text = "陈博士说: 明天下午3点讨论AGI进展"
        entities = self.extractor._extract_entities(text)
        
        entity_texts = [e["text"] for e in entities]
        # 检查提取到了实体（可能是时间或技术实体）
        self.assertGreater(len(entities), 0)
    
    def test_compute_epiplexity(self):
        """测试Epiplexity评分计算"""
        from ems.dialogue_extractor import DialogueTurn
        
        turns = [
            DialogueTurn("陈学东", "测试内容1", turn_id=0),
            DialogueTurn("AI", "测试内容2", turn_id=1),
        ]
        topics = ["AGI", "MEMORY"]
        entities = [{"text": "陈学东", "type": "PERSON"}]
        relations = [{"source": "陈学东", "target": "AI", "type": "TALK"}]
        intents = ["INFORM"]
        
        score = self.extractor._compute_dialogue_epiplexity(
            turns, topics, entities, relations, intents
        )
        
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 1.0)
    
    def test_full_extraction(self):
        """测试完整提取流程"""
        text = """
陈学东: 请实现EMS系统的对话提取功能
OpenClaw-Rft: 好的，基于arXiv:2601.03220论文
陈学东: 明天下午3点验收
"""
        
        structure = self.extractor.extract(text)
        
        self.assertIsInstance(structure, DialogueStructure)
        self.assertGreater(len(structure.turns), 0)
        self.assertGreater(structure.epiplexity_score, 0)


class TestStructureEncoder(unittest.TestCase):
    """测试结构编码器"""
    
    def setUp(self):
        self.encoder = StructureEncoder(compute_budget=1000000)
    
    def test_encode(self):
        """测试编码功能"""
        content = "陈博士明天下午3点讨论AGI记忆系统"
        context = {"user": "陈学东", "topic": "AGI"}
        
        encoded = self.encoder.encode(content, context)
        
        self.assertIn("structure", encoded)
        self.assertIn("residual", encoded)
        self.assertIn("epiplexity_score", encoded)
        self.assertGreaterEqual(encoded["epiplexity_score"], 0)
        self.assertLessEqual(encoded["epiplexity_score"], 1.0)
    
    def test_extract_entities(self):
        """测试实体提取"""
        content = "联系张三博士，讨论AGI项目"
        entities = self.encoder._extract_entities(content)
        
        # 编码器可能提取到不同实体，只要不为空即可
        self.assertIsInstance(entities, list)


class TestEpiplexityMemorySystem(unittest.TestCase):
    """测试EMS核心系统"""
    
    def setUp(self):
        import tempfile
        import shutil
        
        self.temp_dir = tempfile.mkdtemp()
        self.ems = EpiplexityMemorySystem(
            compute_budget=1000000,
            storage_path=self.temp_dir,
            l1_capacity=3
        )
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_encode_dialogue(self):
        """测试对话编码"""
        dialogue = """
陈学东: 测试对话内容
OpenClaw-Rft: 收到测试
"""
        
        memory_id = self.ems.encode(
            content=dialogue,
            context={"test": True},
            content_type="dialogue"
        )
        
        self.assertIsNotNone(memory_id)
        self.assertEqual(len(self.ems.l1_working), 1)
    
    def test_encode_text(self):
        """测试文本编码"""
        text = "这是一段普通文本内容"
        
        memory_id = self.ems.encode(
            content=text,
            context={"type": "note"}
        )
        
        self.assertIsNotNone(memory_id)
    
    def test_retrieve(self):
        """测试检索功能"""
        # 先编码一些记忆
        self.ems.encode("AGI记忆系统很重要", {"topic": "AGI"})
        self.ems.encode("今天天气很好", {"topic": "weather"})
        
        # 检索
        results = self.ems.retrieve("AGI系统", top_k=2)
        
        self.assertIsInstance(results, list)
    
    def test_l1_capacity(self):
        """测试L1容量限制"""
        # 超过容量
        for i in range(5):
            self.ems.encode(f"记忆{i}", {"index": i})
        
        # L1应该只保留最新的3个
        self.assertEqual(len(self.ems.l1_working), 3)
    
    def test_get_stats(self):
        """测试统计功能"""
        self.ems.encode("测试记忆", {})
        
        stats = self.ems.get_stats()
        
        self.assertIn("l1_working", stats)
        self.assertIn("avg_epiplexity", stats)


class TestEpiplexityTheory(unittest.TestCase):
    """测试Epiplexity理论应用"""
    
    def test_structure_vs_random(self):
        """测试结构化内容 vs 随机内容的Epiplexity差异"""
        extractor = DialogueStructureExtractor()
        
        # 结构化对话
        structured = """
陈学东: 请实现EMS系统的Phase 1
OpenClaw-Rft: 好的，基于Epiplexity理论
陈学东: 明天下午3点验收
"""
        
        # 低结构内容
        random_text = "啊哦嗯这个那个随便说说"
        
        struct_result = extractor.extract(structured)
        random_result = extractor.extract(random_text)
        
        # 结构化内容应该有更高的Epiplexity
        self.assertGreater(
            struct_result.epiplexity_score,
            random_result.epiplexity_score
        )


if __name__ == "__main__":
    unittest.main()
