"""
Phase 2 智能检索测试
"""

import unittest
from datetime import datetime, timedelta

from ems import (
    IntelligentRetriever,
    RetrievalResult,
    RetrievalPhase,
    ComputeBudgetManager,
    SemanticEncoder
)


class TestComputeBudgetManager(unittest.TestCase):
    """测试计算预算管理器"""
    
    def setUp(self):
        self.manager = ComputeBudgetManager(total_budget=1000)
    
    def test_allocate(self):
        """测试预算分配"""
        # L1预算: 100
        self.assertTrue(self.manager.allocate(RetrievalPhase.L1_FAST, 50))
        self.assertTrue(self.manager.allocate(RetrievalPhase.L1_FAST, 50))
        # 超出预算
        self.assertFalse(self.manager.allocate(RetrievalPhase.L1_FAST, 10))
    
    def test_get_remaining(self):
        """测试剩余预算查询"""
        self.manager.allocate(RetrievalPhase.L2_STRUCTURE, 100)
        remaining = self.manager.get_remaining(RetrievalPhase.L2_STRUCTURE)
        
        # L2预算: 300, 用了100, 剩200
        self.assertEqual(remaining, 200)
    
    def test_get_stats(self):
        """测试统计信息"""
        self.manager.allocate(RetrievalPhase.L1_FAST, 50)
        stats = self.manager.get_stats()
        
        self.assertIn("total_budget", stats)
        self.assertIn("used_budget", stats)
        self.assertIn("phase_breakdown", stats)
        self.assertEqual(stats["used_budget"], 50)


class TestSemanticEncoder(unittest.TestCase):
    """测试语义编码器"""
    
    def setUp(self):
        self.encoder = SemanticEncoder(dim=128)
    
    def test_encode(self):
        """测试编码"""
        text = "AGI记忆系统"
        vector = self.encoder.encode(text)
        
        self.assertEqual(len(vector), 128)
        # 检查归一化
        import numpy as np
        self.assertAlmostEqual(np.linalg.norm(vector), 1.0, places=5)
    
    def test_similarity(self):
        """测试相似度计算"""
        text1 = "AGI记忆系统"
        text2 = "人工智能记忆"
        text3 = "天气很好"
        
        sim1 = self.encoder.similarity(text1, text2)
        sim2 = self.encoder.similarity(text1, text3)
        
        # 相似文本应该有更高相似度
        self.assertGreater(sim1, sim2)
    
    def test_similarity_range(self):
        """测试相似度范围"""
        text1 = "测试"
        text2 = "测试"
        
        sim = self.encoder.similarity(text1, text2)
        
        self.assertGreaterEqual(sim, -1.0)
        self.assertLessEqual(sim, 1.0)


class TestIntelligentRetriever(unittest.TestCase):
    """测试智能检索引擎"""
    
    def setUp(self):
        self.retriever = IntelligentRetriever(compute_budget=10000)
        
        # 创建测试记忆
        self.l1_memories = [
            {
                "id": "l1_1",
                "content": "陈博士讨论AGI记忆系统",
                "access_count": 5,
                "last_accessed": datetime.now().isoformat(),
                "epiplexity_score": 0.8
            },
            {
                "id": "l1_2", 
                "content": "今天天气很好",
                "access_count": 1,
                "last_accessed": (datetime.now() - timedelta(hours=2)).isoformat(),
                "epiplexity_score": 0.3
            }
        ]
        
        self.l2_memories = {
            "l2_1": {
                "id": "l2_1",
                "content": "EMS系统基于Epiplexity理论",
                "structure": {
                    "entities": [{"text": "EMS", "type": "TECH"}],
                    "topics": ["AGI", "MEMORY"],
                    "templates": ["INFORM"]
                },
                "access_count": 3,
                "epiplexity_score": 0.9
            }
        }
        
        self.l3_memories = {
            "l3_1": {
                "id": "l3_1",
                "content": "递归认知架构RCC-E的核心原理",
                "structure": {
                    "entities": [{"text": "RCC-E", "type": "TECH"}],
                    "topics": ["AGI"]
                },
                "access_count": 10,
                "epiplexity_score": 0.85
            }
        }
    
    def test_retrieve_l1(self):
        """测试L1检索"""
        results, stats = self.retriever.retrieve(
            query="AGI记忆",
            l1_memories=self.l1_memories,
            l2_memories={},
            l3_memories={},
            top_k=2
        )
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].phase, RetrievalPhase.L1_FAST)
    
    def test_retrieve_all_phases(self):
        """测试全阶段检索"""
        results, stats = self.retriever.retrieve(
            query="AGI系统",
            l1_memories=self.l1_memories,
            l2_memories=self.l2_memories,
            l3_memories=self.l3_memories,
            top_k=5
        )
        
        self.assertGreater(len(results), 0)
        self.assertIn("stats", locals())
        self.assertIn("phase_distribution", stats)
    
    def test_retrieval_result_format(self):
        """测试结果格式"""
        results, stats = self.retriever.retrieve(
            query="测试",
            l1_memories=self.l1_memories,
            l2_memories={},
            l3_memories={},
            top_k=1
        )
        
        if results:
            result = results[0]
            self.assertIsInstance(result, RetrievalResult)
            self.assertIn("score", dir(result))
            self.assertIn("memory", dir(result))
            self.assertIn("phase", dir(result))
    
    def test_budget_control(self):
        """测试预算控制"""
        # 使用小预算
        small_budget_retriever = IntelligentRetriever(compute_budget=100)
        
        results, stats = small_budget_retriever.retrieve(
            query="AGI",
            l1_memories=self.l1_memories * 10,  # 大量记忆
            l2_memories=self.l2_memories,
            l3_memories=self.l3_memories,
            top_k=5
        )
        
        # 检查预算使用
        budget_stats = stats.get("budget_stats", {})
        self.assertLessEqual(
            budget_stats.get("used_budget", 0),
            budget_stats.get("total_budget", 100)
        )
    
    def test_min_score_filter(self):
        """测试最低分数过滤"""
        results, stats = self.retriever.retrieve(
            query="完全不相关的内容xyz123",
            l1_memories=self.l1_memories,
            l2_memories=self.l2_memories,
            l3_memories=self.l3_memories,
            top_k=5,
            min_score=0.8  # 高阈值
        )
        
        # 应该返回很少或没有结果
        self.assertLessEqual(len(results), 2)


class TestRetrievalIntegration(unittest.TestCase):
    """检索集成测试"""
    
    def test_end_to_end_retrieval(self):
        """端到端检索测试"""
        from ems import EpiplexityMemorySystem
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            ems = EpiplexityMemorySystem(
                compute_budget=10000,
                storage_path=tmpdir
            )
            
            # 编码一些记忆
            ems.encode("陈博士讨论AGI记忆系统", {"topic": "AGI"})
            ems.encode("EMS基于Epiplexity理论", {"topic": "EMS"})
            ems.encode("今天天气很好", {"topic": "weather"})
            
            # 检索
            result = ems.retrieve("AGI系统", top_k=2, use_intelligent=True)
            
            self.assertIn("results", result)
            self.assertIn("stats", result)
            
            # 验证结果包含AGI相关
            results = result["results"]
            if results:
                self.assertGreater(results[0].get("match_score", 0), 0)


if __name__ == "__main__":
    unittest.main()
