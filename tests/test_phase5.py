"""
Phase 5 AGI集成测试
"""

import unittest
from datetime import datetime

from ems import (
    AGIMemoryBridge,
    RCCEIntegration,
    DistributedMemoryNode,
    SelfImprovement,
    CognitiveState,
    EpiplexityMemorySystem,
    MetacognitiveManager
)


class TestCognitiveState(unittest.TestCase):
    """测试认知状态"""
    
    def test_creation(self):
        """测试创建"""
        state = CognitiveState(
            perception={"content": "用户输入"},
            cognition={"query": "AGI"},
            action={"content": "回复"},
            memory_context={"results": []},
            timestamp=datetime.now().isoformat()
        )
        
        self.assertEqual(state.perception["content"], "用户输入")


class TestRCCEIntegration(unittest.TestCase):
    """测试RCC-E集成"""
    
    def setUp(self):
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.ems = EpiplexityMemorySystem(storage_path=self.temp_dir)
        self.rcc = RCCEIntegration(self.ems)
    
    def test_process_cognitive_cycle(self):
        """测试认知周期处理"""
        state = self.rcc.process_cognitive_cycle(
            perception_input={"content": "用户问AGI", "importance": 0.8},
            cognition_result={"query": "AGI是什么"},
            action_output={"content": "AGI是通用人工智能", "status": "success"}
        )
        
        self.assertIsInstance(state, CognitiveState)
        self.assertEqual(len(self.rcc.cognitive_history), 1)
    
    def test_get_cognitive_context(self):
        """测试获取认知上下文"""
        # 先添加一些记忆
        self.ems.encode("AGI记忆系统", {"topic": "AGI"})
        
        context = self.rcc.get_cognitive_context("AGI")
        
        self.assertIn("retrieved_memories", context)
        self.assertIn("recent_cognitive_history", context)
    
    def test_feedback_hook(self):
        """测试反馈钩子"""
        hooks_called = []
        
        def test_hook(state):
            hooks_called.append(state)
        
        self.rcc.register_feedback_hook(test_hook)
        
        self.rcc.process_cognitive_cycle(
            perception_input={"content": "test"},
            cognition_result={},
            action_output={}
        )
        
        self.assertEqual(len(hooks_called), 1)


class TestDistributedMemoryNode(unittest.TestCase):
    """测试分布式记忆节点"""
    
    def setUp(self):
        import tempfile
        self.temp_dir1 = tempfile.mkdtemp()
        self.temp_dir2 = tempfile.mkdtemp()
        
        self.ems1 = EpiplexityMemorySystem(storage_path=self.temp_dir1)
        self.ems2 = EpiplexityMemorySystem(storage_path=self.temp_dir2)
        
        self.node1 = DistributedMemoryNode("node1", self.ems1)
        self.node2 = DistributedMemoryNode("node2", self.ems2)
    
    def test_connect_peer(self):
        """测试连接对等节点"""
        self.node1.connect_peer(self.node2)
        
        self.assertIn("node2", self.node1.peers)
    
    def test_share_memory(self):
        """测试共享记忆"""
        self.node1.connect_peer(self.node2)
        
        # 在node1创建记忆
        memory_id = self.ems1.encode("共享测试记忆", {"shared": True})
        self.ems1.l2_episodic[memory_id] = self.ems1.l1_working.pop()
        
        # 共享到node2
        result = self.node1.share_memory(memory_id)
        
        self.assertTrue(result)
        self.assertIn(memory_id, self.node2.shared_memories)
    
    def test_query_distributed(self):
        """测试分布式查询"""
        self.node1.connect_peer(self.node2)
        
        # 添加共享记忆
        self.node2.shared_memories["shared1"] = {
            "memory": {"content": "共享AGI记忆"},
            "from_node": "node2",
            "received_at": datetime.now().isoformat()
        }
        
        results = self.node1.query_distributed("AGI")
        
        self.assertIn("local", results)
        self.assertIn("peers", results)


class TestSelfImprovement(unittest.TestCase):
    """测试自我改进系统"""
    
    def setUp(self):
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.ems = EpiplexityMemorySystem(storage_path=self.temp_dir)
        self.meta = MetacognitiveManager()
        self.improvement = SelfImprovement(self.ems, self.meta)
        
        # 添加一些测试记忆
        for i in range(10):
            self.ems.encode(f"测试记忆{i}", {"index": i})
    
    def test_analyze_memory_efficiency(self):
        """测试记忆效率分析"""
        analysis = self.improvement.analyze_memory_efficiency()
        
        self.assertIn("total_memories", analysis)
        self.assertIn("recommendations", analysis)
    
    def test_suggest_optimizations(self):
        """测试优化建议"""
        suggestions = self.improvement.suggest_optimizations()
        
        self.assertIsInstance(suggestions, list)
    
    def test_analyze_access_patterns(self):
        """测试访问模式分析"""
        patterns = self.improvement._analyze_access_patterns()
        
        self.assertIn("frequent_topics", patterns)
    
    def test_analyze_epiplexity_distribution(self):
        """测试Epiplexity分布分析"""
        dist = self.improvement._analyze_epiplexity_distribution()
        
        self.assertIn("high_count", dist)
        self.assertIn("medium_count", dist)
        self.assertIn("low_count", dist)


class TestAGIMemoryBridge(unittest.TestCase):
    """测试AGI记忆桥接器"""
    
    def setUp(self):
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.ems = EpiplexityMemorySystem(storage_path=self.temp_dir)
        self.bridge = AGIMemoryBridge(self.ems)
    
    def test_on_user_message(self):
        """测试处理用户消息"""
        result = self.bridge.on_user_message("你好，讨论AGI", "陈博士")
        
        self.assertIn("memory_id", result)
        self.assertIn("retrieval", result)
        self.assertIn("context", result)
    
    def test_on_assistant_response(self):
        """测试处理助手回复"""
        memory_id = self.bridge.on_assistant_response("AGI是通用人工智能")
        
        self.assertIsNotNone(memory_id)
    
    def test_get_system_status(self):
        """测试获取系统状态"""
        status = self.bridge.get_system_status()
        
        self.assertIn("ems_stats", status)
        self.assertIn("cognitive_cycles", status)
    
    def test_initialize_metacognition(self):
        """测试初始化元认知"""
        meta = MetacognitiveManager()
        self.bridge.initialize_metacognition(meta)
        
        self.assertIsNotNone(self.bridge.self_improvement)
        
        # 现在应该能获取更详细的状态
        status = self.bridge.get_system_status()
        self.assertIn("memory_efficiency", status)


class TestPhase5Integration(unittest.TestCase):
    """Phase 5集成测试"""
    
    def test_full_agimemory_workflow(self):
        """完整AGI记忆工作流"""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. 创建EMS
            ems = EpiplexityMemorySystem(storage_path=tmpdir)
            
            # 2. 创建桥接器
            bridge = AGIMemoryBridge(ems)
            
            # 3. 初始化元认知
            meta = MetacognitiveManager()
            bridge.initialize_metacognition(meta)
            
            # 4. 模拟对话
            result1 = bridge.on_user_message("讨论AGI记忆系统", "陈博士")
            bridge.on_assistant_response("AGI记忆系统基于Epiplexity理论", result1["memory_id"])
            
            result2 = bridge.on_user_message("如何实现", "陈博士")
            bridge.on_assistant_response("需要5个Phase逐步实现", result2["memory_id"])
            
            # 5. 运行维护
            maintenance = bridge.run_maintenance()
            
            self.assertIn("consolidation", maintenance)
            self.assertIn("status", maintenance)
            
            # 6. 检查系统状态
            status = bridge.get_system_status()
            self.assertGreater(status["ems_stats"]["total_memories"], 0)


if __name__ == "__main__":
    unittest.main()
