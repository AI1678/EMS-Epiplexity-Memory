"""
Phase 3 自动巩固测试
"""

import unittest
from datetime import datetime, timedelta

from ems import (
    SleepConsolidator,
    PatternMiner,
    MemoryCompressor,
    Pattern,
    AbstractMemory
)


class TestPatternMiner(unittest.TestCase):
    """测试模式挖掘器"""
    
    def setUp(self):
        self.miner = PatternMiner(min_frequency=2)
        
        # 创建测试记忆
        self.memories = [
            {
                "id": "m1",
                "structure": {
                    "entities": [
                        {"text": "陈博士", "type": "PERSON"},
                        {"text": "AGI", "type": "TECH"}
                    ],
                    "relations": [{"type": "DISCUSS", "source": "陈博士", "target": "AGI"}],
                    "templates": ["INFORM"],
                    "topics": ["AGI", "MEMORY"]
                }
            },
            {
                "id": "m2",
                "structure": {
                    "entities": [
                        {"text": "陈博士", "type": "PERSON"},
                        {"text": "EMS", "type": "TECH"}
                    ],
                    "relations": [{"type": "DISCUSS", "source": "陈博士", "target": "EMS"}],
                    "templates": ["INFORM"],
                    "topics": ["AGI", "SYSTEM"]
                }
            },
            {
                "id": "m3",
                "structure": {
                    "entities": [
                        {"text": "OpenClaw", "type": "AI"},
                        {"text": "AGI", "type": "TECH"}
                    ],
                    "relations": [],
                    "templates": ["QUESTION"],
                    "topics": ["AGI"]
                }
            }
        ]
    
    def test_mine_entity_patterns(self):
        """测试实体模式挖掘"""
        patterns = self.miner._mine_entity_patterns(self.memories)
        
        # 陈博士出现2次，应该被挖掘
        chen_patterns = [p for p in patterns if p.content.get("text") == "陈博士"]
        self.assertEqual(len(chen_patterns), 1)
        self.assertEqual(chen_patterns[0].frequency, 2)
    
    def test_mine_topic_patterns(self):
        """测试主题模式挖掘"""
        patterns = self.miner._mine_topic_patterns(self.memories)
        
        # AGI出现3次
        agi_patterns = [p for p in patterns if p.content == "AGI"]
        self.assertEqual(len(agi_patterns), 1)
        self.assertEqual(agi_patterns[0].frequency, 3)
    
    def test_mine_patterns(self):
        """测试完整模式挖掘"""
        patterns = self.miner.mine_patterns(self.memories)
        
        self.assertIn("entities", patterns)
        self.assertIn("topics", patterns)
        self.assertIn("templates", patterns)
        
        # 检查AGI主题
        topic_patterns = patterns["topics"]
        self.assertGreater(len(topic_patterns), 0)


class TestMemoryCompressor(unittest.TestCase):
    """测试记忆压缩器"""
    
    def setUp(self):
        self.compressor = MemoryCompressor()
        
        self.patterns = {
            "entities": [
                Pattern("entity", {"text": "陈博士", "type": "PERSON"}, 3, 0.9, ["m1", "m2", "m3"])
            ],
            "topics": [
                Pattern("topic", "AGI", 3, 0.95, ["m1", "m2", "m3"])
            ],
            "templates": [],
            "relations": []
        }
        
        self.memories = [
            {"id": "m1", "content": "记忆1"},
            {"id": "m2", "content": "记忆2"},
            {"id": "m3", "content": "记忆3"}
        ]
    
    def test_compress(self):
        """测试压缩"""
        abstract = self.compressor.compress(self.memories, self.patterns)
        
        self.assertIsInstance(abstract, AbstractMemory)
        self.assertEqual(abstract.source_count, 3)
        self.assertGreater(abstract.epiplexity_score, 0)
        self.assertIn("陈博士", abstract.summary)
    
    def test_generate_summary(self):
        """测试摘要生成"""
        summary = self.compressor._generate_summary(self.memories, self.patterns)
        
        self.assertIn("AGI", summary)
        self.assertIn("陈博士", summary)


class TestSleepConsolidator(unittest.TestCase):
    """测试睡眠巩固器"""
    
    def setUp(self):
        self.consolidator = SleepConsolidator(min_memories_for_consolidation=3)
        
        self.l2_memories = {
            "m1": {
                "id": "m1",
                "content": "陈博士讨论AGI",
                "structure": {
                    "entities": [{"text": "陈博士", "type": "PERSON"}],
                    "topics": ["AGI"],
                    "templates": ["INFORM"],
                    "relations": []
                }
            },
            "m2": {
                "id": "m2",
                "content": "陈博士讨论EMS",
                "structure": {
                    "entities": [{"text": "陈博士", "type": "PERSON"}],
                    "topics": ["AGI"],
                    "templates": ["INFORM"],
                    "relations": []
                }
            },
            "m3": {
                "id": "m3",
                "content": "OpenClaw讨论AGI",
                "structure": {
                    "entities": [{"text": "OpenClaw", "type": "AI"}],
                    "topics": ["AGI"],
                    "templates": ["QUESTION"],
                    "relations": []
                }
            }
        }
        
        self.l3_memories = {}
    
    def test_should_consolidate(self):
        """测试是否应该巩固"""
        # 记忆数不足
        self.assertFalse(self.consolidator.should_consolidate(2))
        
        # 记忆数足够
        self.assertTrue(self.consolidator.should_consolidate(5))
    
    def test_consolidate(self):
        """测试巩固过程"""
        result = self.consolidator.consolidate(
            l2_memories=self.l2_memories,
            l3_memories=self.l3_memories
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("abstract_memories_created", result)
        
        # 检查L3是否添加了抽象记忆
        self.assertGreater(len(self.l3_memories), 0)
    
    def test_consolidate_insufficient_memories(self):
        """测试记忆不足时的处理"""
        consolidator = SleepConsolidator(min_memories_for_consolidation=10)
        
        result = consolidator.consolidate(
            l2_memories=self.l2_memories,
            l3_memories=self.l3_memories
        )
        
        self.assertEqual(result["status"], "skipped")
    
    def test_cluster_memories(self):
        """测试记忆聚类"""
        memories = list(self.l2_memories.values())
        clusters = self.consolidator._cluster_memories(memories)
        
        # 应该按主题聚类
        self.assertIn("AGI", clusters)


class TestPattern(unittest.TestCase):
    """测试Pattern数据类"""
    
    def test_pattern_creation(self):
        """测试模式创建"""
        pattern = Pattern(
            pattern_type="entity",
            content={"text": "AGI", "type": "TECH"},
            frequency=5,
            confidence=0.9,
            source_memories=["m1", "m2", "m3", "m4", "m5"]
        )
        
        self.assertEqual(pattern.pattern_type, "entity")
        self.assertEqual(pattern.frequency, 5)
        self.assertEqual(len(pattern.source_memories), 5)
    
    def test_pattern_to_dict(self):
        """测试模式序列化"""
        pattern = Pattern("topic", "AGI", 3, 0.8, ["m1", "m2", "m3"])
        d = pattern.to_dict()
        
        self.assertEqual(d["pattern_type"], "topic")
        self.assertEqual(d["content"], "AGI")


class TestAbstractMemory(unittest.TestCase):
    """测试AbstractMemory数据类"""
    
    def test_abstract_memory_creation(self):
        """测试抽象记忆创建"""
        patterns = [
            Pattern("topic", "AGI", 5, 0.9, ["m1", "m2", "m3", "m4", "m5"])
        ]
        
        abstract = AbstractMemory(
            id="abstract_123",
            created_at=datetime.now().isoformat(),
            pattern_type="consolidated",
            summary="AGI研究摘要",
            patterns=patterns,
            source_count=5,
            epiplexity_score=0.85,
            metadata={"compression_ratio": 0.5}
        )
        
        self.assertEqual(abstract.source_count, 5)
        self.assertEqual(len(abstract.patterns), 1)
    
    def test_to_dict(self):
        """测试序列化"""
        abstract = AbstractMemory(
            id="test",
            created_at="2024-01-01",
            pattern_type="test",
            summary="test summary",
            patterns=[],
            source_count=0,
            epiplexity_score=0.5,
            metadata={}
        )
        
        d = abstract.to_dict()
        self.assertEqual(d["id"], "test")
        self.assertEqual(d["summary"], "test summary")


class TestPhase3Integration(unittest.TestCase):
    """Phase 3集成测试"""
    
    def test_end_to_end_consolidation(self):
        """端到端巩固测试"""
        from ems import EpiplexityMemorySystem
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            ems = EpiplexityMemorySystem(
                compute_budget=10000,
                storage_path=tmpdir
            )
            
            # 编码多个相关记忆
            for i in range(5):
                ems.encode(
                    f"陈博士讨论AGI记忆系统第{i+1}次",
                    {"topic": "AGI", "session": i}
                )
            
            # 触发巩固
            result = ems.consolidate(use_sleep_mode=True)
            
            self.assertIn("sleep_consolidation", result)
            
            # 检查是否生成了抽象记忆
            if result["sleep_consolidation"]["status"] == "success":
                self.assertGreater(
                    result["sleep_consolidation"]["abstract_memories_created"],
                    0
                )


if __name__ == "__main__":
    unittest.main()
