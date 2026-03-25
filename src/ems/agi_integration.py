"""
AGI集成系统

Phase 5: EMS与RCC-E框架深度融合
实现递归认知闭环和分布式记忆网络
"""

import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CognitiveState:
    """认知状态"""
    perception: Dict[str, Any]      # 感知输入
    cognition: Dict[str, Any]       # 认知处理
    action: Dict[str, Any]          # 行动输出
    memory_context: Dict[str, Any]  # 记忆上下文
    timestamp: str


class RCCEIntegration:
    """
    RCC-E框架集成器
    
    将EMS嵌入递归认知闭环
    Perception → Cognition → Action → Memory → Feedback
    """
    
    def __init__(self, ems_instance):
        self.ems = ems_instance
        self.cognitive_history: List[CognitiveState] = []
        self.feedback_hooks: List[Callable] = []
    
    def process_cognitive_cycle(
        self,
        perception_input: Dict[str, Any],
        cognition_result: Dict[str, Any],
        action_output: Dict[str, Any]
    ) -> CognitiveState:
        """
        处理一个认知周期
        
        将认知周期的结果存入记忆，并提供记忆上下文
        """
        # 1. 编码感知输入到记忆
        if "content" in perception_input:
            self.ems.encode(
                content=perception_input["content"],
                context={
                    "type": "perception",
                    "timestamp": datetime.now().isoformat()
                },
                importance=perception_input.get("importance", 0.5)
            )
        
        # 2. 检索相关记忆作为上下文
        if "query" in cognition_result:
            retrieval_result = self.ems.retrieve(
                query=cognition_result["query"],
                top_k=3
            )
            memory_context = retrieval_result
        else:
            memory_context = {"results": []}
        
        # 3. 编码行动结果
        if "content" in action_output:
            self.ems.encode(
                content=action_output["content"],
                context={
                    "type": "action",
                    "result": action_output.get("status", "unknown")
                },
                importance=action_output.get("importance", 0.5)
            )
        
        # 4. 创建认知状态
        state = CognitiveState(
            perception=perception_input,
            cognition=cognition_result,
            action=action_output,
            memory_context=memory_context,
            timestamp=datetime.now().isoformat()
        )
        
        self.cognitive_history.append(state)
        
        # 5. 触发反馈钩子
        for hook in self.feedback_hooks:
            hook(state)
        
        return state
    
    def get_cognitive_context(self, query: str) -> Dict[str, Any]:
        """获取认知上下文（记忆增强）"""
        # 检索相关记忆
        retrieval = self.ems.retrieve(query, top_k=5)
        
        # 获取最近的认知历史
        recent_history = self.cognitive_history[-5:] if len(self.cognitive_history) >= 5 else self.cognitive_history
        
        return {
            "retrieved_memories": retrieval,
            "recent_cognitive_history": [
                {
                    "perception": h.perception.get("content", "")[:100],
                    "action": h.action.get("content", "")[:100],
                    "timestamp": h.timestamp
                }
                for h in recent_history
            ]
        }
    
    def register_feedback_hook(self, hook: Callable):
        """注册反馈钩子"""
        self.feedback_hooks.append(hook)


class DistributedMemoryNode:
    """
    分布式记忆节点
    
    支持多节点记忆共享
    """
    
    def __init__(self, node_id: str, ems_instance):
        self.node_id = node_id
        self.ems = ems_instance
        self.peers: Dict[str, 'DistributedMemoryNode'] = {}
        self.shared_memories: Dict[str, Any] = {}
    
    def connect_peer(self, peer_node: 'DistributedMemoryNode'):
        """连接对等节点"""
        self.peers[peer_node.node_id] = peer_node
    
    def share_memory(
        self,
        memory_id: str,
        target_nodes: Optional[List[str]] = None
    ) -> bool:
        """
        共享记忆到其他节点
        
        Args:
            memory_id: 要共享的记忆ID
            target_nodes: 目标节点ID列表（None表示所有节点）
        """
        # 查找记忆
        memory = None
        for layer in [self.ems.l2_episodic, self.ems.l3_semantic]:
            if memory_id in layer:
                memory = layer[memory_id]
                break
        
        if not memory:
            return False
        
        # 确定目标节点
        targets = target_nodes or list(self.peers.keys())
        
        # 共享记忆
        for target_id in targets:
            if target_id in self.peers:
                peer = self.peers[target_id]
                peer.receive_shared_memory(memory_id, memory, self.node_id)
        
        return True
    
    def receive_shared_memory(
        self,
        memory_id: str,
        memory: Dict,
        from_node: str
    ):
        """接收共享记忆"""
        self.shared_memories[memory_id] = {
            "memory": memory,
            "from_node": from_node,
            "received_at": datetime.now().isoformat()
        }
    
    def query_distributed(
        self,
        query: str,
        include_shared: bool = True
    ) -> Dict[str, Any]:
        """
        分布式查询
        
        查询本地和所有对等节点的记忆
        """
        results = {
            "local": self.ems.retrieve(query, top_k=3),
            "peers": {}
        }
        
        if include_shared:
            # 查询共享记忆
            for mem_id, shared in self.shared_memories.items():
                memory = shared["memory"]
                if query.lower() in memory.get("content", "").lower():
                    results["peers"][mem_id] = {
                        "memory": memory,
                        "from_node": shared["from_node"]
                    }
        
        return results


class SelfImprovement:
    """
    自我改进系统
    
    基于记忆分析实现系统自我优化
    """
    
    def __init__(self, ems_instance, metacognitive_manager):
        self.ems = ems_instance
        self.meta = metacognitive_manager
        self.improvement_log: List[Dict] = []
    
    def analyze_memory_efficiency(self) -> Dict[str, Any]:
        """
        分析记忆效率
        
        识别记忆系统的优化机会
        """
        report = self.meta.get_memory_report(self.ems.l3_semantic)
        
        # 分析指标
        analysis = {
            "total_memories": report["total_memories"],
            "high_value_ratio": report["value_distribution"].get("high", 0) / max(1, report["total_memories"]),
            "garbage_ratio": report["value_distribution"].get("low", 0) / max(1, report["total_memories"]),
            "critical_memories": report["critical_memories"],
            "recommendations": []
        }
        
        # 生成建议
        if analysis["garbage_ratio"] > 0.3:
            analysis["recommendations"].append("垃圾记忆比例过高，建议运行遗忘周期")
        
        if analysis["high_value_ratio"] < 0.2:
            analysis["recommendations"].append("高价值记忆比例偏低，建议优化编码策略")
        
        if report["total_memories"] > 1000:
            analysis["recommendations"].append("记忆数量过多，建议加强巩固和压缩")
        
        return analysis
    
    def suggest_optimizations(self) -> List[Dict]:
        """生成优化建议"""
        suggestions = []
        
        # 分析访问模式
        access_patterns = self._analyze_access_patterns()
        
        if access_patterns["frequent_topics"]:
            suggestions.append({
                "type": "cache_optimization",
                "description": f"发现高频主题: {access_patterns['frequent_topics']}",
                "action": "增加相关记忆的L1容量"
            })
        
        # 分析Epiplexity分布
        epiplexity_dist = self._analyze_epiplexity_distribution()
        
        if epiplexity_dist["low_count"] > epiplexity_dist["high_count"]:
            suggestions.append({
                "type": "encoding_optimization",
                "description": "低Epiplexity记忆过多",
                "action": "优化内容类型检测和结构提取"
            })
        
        return suggestions
    
    def _analyze_access_patterns(self) -> Dict[str, Any]:
        """分析访问模式"""
        topic_counts = {}
        
        for memory in list(self.ems.l2_episodic.values()) + list(self.ems.l3_semantic.values()):
            access_count = memory.get("access_count", 0)
            if access_count > 5:  # 高频访问
                topics = memory.get("structure", {}).get("topics", [])
                for topic in topics:
                    topic_counts[topic] = topic_counts.get(topic, 0) + access_count
        
        # 排序
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "frequent_topics": [t[0] for t in sorted_topics[:3]],
            "topic_distribution": dict(sorted_topics)
        }
    
    def _analyze_epiplexity_distribution(self) -> Dict[str, int]:
        """分析Epiplexity分布"""
        high = 0
        medium = 0
        low = 0
        
        for memory in list(self.ems.l2_episodic.values()) + list(self.ems.l3_semantic.values()):
            ep = memory.get("epiplexity_score", 0.5)
            if ep >= 0.7:
                high += 1
            elif ep >= 0.4:
                medium += 1
            else:
                low += 1
        
        return {"high_count": high, "medium_count": medium, "low_count": low}
    
    def apply_improvement(self, improvement_type: str) -> bool:
        """
        应用改进
        
        Args:
            improvement_type: 改进类型
            
        Returns:
            是否成功应用
        """
        if improvement_type == "run_forgetting":
            result = self.meta.run_forgetting_cycle(self.ems.l2_episodic)
            self.improvement_log.append({
                "type": improvement_type,
                "timestamp": datetime.now().isoformat(),
                "result": result
            })
            return True
        
        elif improvement_type == "consolidate":
            result = self.ems.consolidate(use_sleep_mode=True)
            self.improvement_log.append({
                "type": improvement_type,
                "timestamp": datetime.now().isoformat(),
                "result": result
            })
            return True
        
        return False


class AGIMemoryBridge:
    """
    AGI记忆桥接器
    
    将EMS与OpenClaw-Rft AGI系统集成
    """
    
    def __init__(self, ems_instance):
        self.ems = ems_instance
        self.rcc_integration = RCCEIntegration(ems_instance)
        self.self_improvement = None  # 需要metacognitive_manager初始化
    
    def initialize_metacognition(self, meta_manager):
        """初始化元认知系统"""
        self.self_improvement = SelfImprovement(self.ems, meta_manager)
    
    def on_user_message(self, message: str, user_id: str = "user") -> Dict[str, Any]:
        """
        处理用户消息（AGI入口）
        
        自动编码到记忆，并检索相关上下文
        """
        # 1. 编码用户消息
        memory_id = self.ems.encode(
            content=f"{user_id}: {message}",
            context={"type": "user_message", "user": user_id},
            content_type="dialogue"
        )
        
        # 2. 检索相关记忆
        retrieval = self.ems.retrieve(message, top_k=5, use_intelligent=True)
        
        # 3. 获取认知上下文
        context = self.rcc_integration.get_cognitive_context(message)
        
        return {
            "memory_id": memory_id,
            "retrieval": retrieval,
            "context": context
        }
    
    def on_assistant_response(
        self,
        response: str,
        related_memory_id: str = None
    ) -> str:
        """
        处理助手回复
        
        编码回复到记忆
        """
        memory_id = self.ems.encode(
            content=f"OpenClaw-Rft: {response}",
            context={
                "type": "assistant_response",
                "related_to": related_memory_id
            },
            content_type="dialogue"
        )
        
        return memory_id
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        stats = self.ems.get_stats()
        
        status = {
            "ems_stats": stats,
            "cognitive_cycles": len(self.rcc_integration.cognitive_history),
        }
        
        if self.self_improvement:
            status["memory_efficiency"] = self.self_improvement.analyze_memory_efficiency()
            status["optimization_suggestions"] = self.self_improvement.suggest_optimizations()
        
        return status
    
    def run_maintenance(self) -> Dict[str, Any]:
        """
        运行系统维护
        
        包括：巩固、遗忘、自我改进
        """
        results = {}
        
        # 1. 记忆巩固
        results["consolidation"] = self.ems.consolidate(use_sleep_mode=True)
        
        # 2. 元认知遗忘（如果有）
        if self.self_improvement:
            results["forgetting"] = self.self_improvement.meta.run_forgetting_cycle(
                self.ems.l2_episodic
            )
        
        # 3. 生成报告
        results["status"] = self.get_system_status()
        
        return results
