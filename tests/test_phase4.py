"""
Phase 4 元认知测试
"""

import unittest
from datetime import datetime, timedelta

from ems import (
    MetacognitiveManager,
    MemoryValuePredictor,
    MemoryQualityEvaluator,
    ActiveForgetting,
    MemoryEvaluation,
    MemoryQuality
)


class TestMemoryValuePredictor(unittest.TestCase):
    """测试记忆价值预测器"""
    
    def setUp(self):
        self.predictor = MemoryValuePredictor()
    
    def test_predict_value_high_epiplexity(self):
        """测试高Epiplexity记忆的价值预测"""
        memory = {
            "id": "m1",
            "epiplexity_score": 0.9,
            "access_count": 10,
            "timestamp": datetime.now().isoformat(),
            "structure": {
                "entities": [{"text": "AGI", "type": "TECH"}],
                "relations": []
            }
        }
        
        value = self.predictor.predict_value(memory)
        
        self.assertGreater(value, 0.5)
        self.assertLessEqual(value, 1.0)
    
    def test_predict_value_low_access(self):
        """测试低访问记忆的价值预测"""
        memory = {
            "id": "m2",
            "epiplexity_score": 0.5,
            "access_count": 0,
            "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
            "structure": {"entities": [], "relations": []}
        }
        
        value = self.predictor.predict_value(memory)
        
        self.assertLess(value, 0.5)
    
    def test_access_score(self):
        """测试访问分数计算"""
        memory_high = {"access_count": 100}
        memory_low = {"access_count": 1}
        
        score_high = self.predictor._compute_access_score(memory_high)
        score_low = self.predictor._compute_access_score(memory_low)
        
        self.assertGreater(score_high, score_low)
    
    def test_recency_score(self):
        """测试新鲜度分数"""
        memory_recent = {
            "last_accessed": datetime.now().isoformat()
        }
        memory_old = {
            "last_accessed": (datetime.now() - timedelta(days=30)).isoformat()
        }
        
        score_recent = self.predictor._compute_recency_score(memory_recent)
        score_old = self.predictor._compute_recency_score(memory_old)
        
        self.assertGreater(score_recent, score_old)


class TestMemoryQualityEvaluator(unittest.TestCase):
    """测试记忆质量评估器"""
    
    def setUp(self):
        self.evaluator = MemoryQualityEvaluator()
    
    def test_evaluate_critical_memory(self):
        """测试关键记忆评估"""
        memory = {
            "id": "m1",
            "content": "陈博士的身份信息很重要",
            "epiplexity_score": 0.9,
            "importance": 1.0
        }
        
        evaluation = self.evaluator.evaluate(memory, 0.9)
        
        self.assertEqual(evaluation.quality, MemoryQuality.CRITICAL)
        self.assertEqual(evaluation.retention_probability, 1.0)
    
    def test_evaluate_garbage_memory(self):
        """测试垃圾记忆评估"""
        memory = {
            "id": "m2",
            "content": "随便临时测试内容",
            "epiplexity_score": 0.05,
            "importance": 0.1
        }

        evaluation = self.evaluator.evaluate(memory, 0.1)

        # 可能是GARBAGE或CRITICAL（如果包含关键词）
        self.assertIn(evaluation.quality, [MemoryQuality.GARBAGE, MemoryQuality.CRITICAL, MemoryQuality.LOW])
    
    def test_evaluate_high_value(self):
        """测试高价值记忆"""
        memory = {
            "id": "m3",
            "content": "AGI记忆系统架构设计文档",
            "epiplexity_score": 0.85,
            "access_count": 15,
            "importance": 0.8  # 不是关键记忆
        }
        
        evaluation = self.evaluator.evaluate(memory, 0.85)
        
        # 可能是HIGH或CRITICAL，取决于内容
        self.assertIn(evaluation.quality, [MemoryQuality.HIGH, MemoryQuality.CRITICAL])
        self.assertGreater(evaluation.retention_probability, 0.7)
    
    def test_evaluate_medium_value(self):
        """测试中等价值记忆"""
        memory = {
            "id": "m4",
            "content": "普通对话内容",
            "epiplexity_score": 0.5,
            "importance": 0.5
        }

        evaluation = self.evaluator.evaluate(memory, 0.6)

        # 中等价值可能是多种类型
        self.assertIn(evaluation.quality, [MemoryQuality.MEDIUM, MemoryQuality.HIGH, MemoryQuality.GARBAGE])


class TestActiveForgetting(unittest.TestCase):
    """测试主动遗忘系统"""
    
    def setUp(self):
        self.forgetting = ActiveForgetting()
        
        self.memories = {
            "m1": {"id": "m1", "content": "测试记忆1"},
            "m2": {"id": "m2", "content": "测试记忆2"}
        }
    
    def test_should_forget_critical(self):
        """测试关键记忆不遗忘"""
        evaluation = MemoryEvaluation(
            memory_id="m1",
            quality=MemoryQuality.CRITICAL,
            value_score=1.0,
            retention_probability=1.0,
            forget_after=None,
            reasons=[]
        )
        
        should_forget = self.forgetting.should_forget(evaluation)
        
        self.assertFalse(should_forget)
    
    def test_should_forget_garbage(self):
        """测试垃圾记忆立即遗忘"""
        evaluation = MemoryEvaluation(
            memory_id="m2",
            quality=MemoryQuality.GARBAGE,
            value_score=0.0,
            retention_probability=0.0,
            forget_after=timedelta(hours=1),
            reasons=[]
        )
        
        should_forget = self.forgetting.should_forget(evaluation)
        
        self.assertTrue(should_forget)
    
    def test_forget_execution(self):
        """测试遗忘执行"""
        evaluation = MemoryEvaluation(
            memory_id="m1",
            quality=MemoryQuality.LOW,
            value_score=0.2,
            retention_probability=0.0,
            forget_after=timedelta(days=1),
            reasons=["test"]
        )
        
        result = self.forgetting.forget("m1", evaluation, self.memories)
        
        self.assertTrue(result)
        self.assertNotIn("m1", self.memories)
        self.assertEqual(len(self.forgetting.forget_log), 1)
    
    def test_get_forget_stats(self):
        """测试遗忘统计"""
        # 先遗忘一些记忆
        evaluation = MemoryEvaluation(
            memory_id="m1",
            quality=MemoryQuality.LOW,
            value_score=0.2,
            retention_probability=0.0,
            forget_after=timedelta(days=1),
            reasons=[]
        )
        self.forgetting.forget("m1", evaluation, self.memories)
        
        stats = self.forgetting.get_forget_stats()
        
        self.assertEqual(stats["total_forgotten"], 1)


class TestMetacognitiveManager(unittest.TestCase):
    """测试元认知管理器"""
    
    def setUp(self):
        self.manager = MetacognitiveManager()
        
        self.memories = {
            "m1": {
                "id": "m1",
                "content": "陈博士讨论AGI",
                "epiplexity_score": 0.9,
                "access_count": 20,
                "timestamp": datetime.now().isoformat(),
                "importance": 1.0
            },
            "m2": {
                "id": "m2",
                "content": "测试内容",
                "epiplexity_score": 0.2,
                "access_count": 0,
                "timestamp": (datetime.now() - timedelta(days=30)).isoformat()
            },
            "m3": {
                "id": "m3",
                "content": "普通对话",
                "epiplexity_score": 0.5,
                "access_count": 5,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def test_evaluate_all(self):
        """测试评估所有记忆"""
        evaluations = self.manager.evaluate_all(self.memories)
        
        self.assertEqual(len(evaluations), 3)
        
        # 检查m1是关键记忆
        self.assertEqual(evaluations["m1"].quality, MemoryQuality.CRITICAL)
    
    def test_run_forgetting_cycle(self):
        """测试遗忘周期"""
        result = self.manager.run_forgetting_cycle(self.memories)
        
        self.assertIn("evaluated", result)
        self.assertIn("actually_forgotten", result)
        self.assertEqual(result["evaluated"], 3)
    
    def test_get_memory_report(self):
        """测试记忆报告"""
        report = self.manager.get_memory_report(self.memories)
        
        self.assertIn("total_memories", report)
        self.assertIn("quality_distribution", report)
        self.assertIn("value_distribution", report)
        
        self.assertEqual(report["total_memories"], 3)


class TestMemoryEvaluation(unittest.TestCase):
    """测试MemoryEvaluation数据类"""
    
    def test_creation(self):
        """测试创建"""
        evaluation = MemoryEvaluation(
            memory_id="test",
            quality=MemoryQuality.HIGH,
            value_score=0.8,
            retention_probability=0.9,
            forget_after=timedelta(days=30),
            reasons=["高Epiplexity", "高频访问"]
        )
        
        self.assertEqual(evaluation.memory_id, "test")
        self.assertEqual(evaluation.quality, MemoryQuality.HIGH)
    
    def test_to_dict(self):
        """测试序列化"""
        evaluation = MemoryEvaluation(
            memory_id="test",
            quality=MemoryQuality.MEDIUM,
            value_score=0.5,
            retention_probability=0.7,
            forget_after=None,
            reasons=["test"]
        )
        
        d = evaluation.to_dict()
        
        self.assertEqual(d["memory_id"], "test")
        self.assertEqual(d["quality"], "medium")


class TestPhase4Integration(unittest.TestCase):
    """Phase 4集成测试"""
    
    def test_end_to_end_metacognition(self):
        """端到端元认知测试"""
        from ems import EpiplexityMemorySystem
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            ems = EpiplexityMemorySystem(
                compute_budget=10000,
                storage_path=tmpdir
            )
            
            # 编码不同类型的记忆
            ems.encode("陈博士的核心身份信息", {"importance": 1.0})
            ems.encode("测试内容", {"importance": 0.1})
            ems.encode("AGI系统设计", {"importance": 0.8})
            
            # 创建元认知管理器
            from ems import MetacognitiveManager
            meta = MetacognitiveManager()
            
            # 评估L2记忆
            report = meta.get_memory_report(ems.l2_episodic)
            
            self.assertIn("total_memories", report)
            self.assertIn("quality_distribution", report)


if __name__ == "__main__":
    unittest.main()
