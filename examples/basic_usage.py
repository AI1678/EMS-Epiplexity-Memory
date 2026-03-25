# 使用示例

## 基础用法

```python
from ems import EpiplexityMemorySystem

# 初始化EMS
ems = EpiplexityMemorySystem(
    compute_budget=1_000_000,
    storage_path="./memory_store"
)

# 编码记忆
memory_id = ems.encode(
    content="陈博士说: 明天下午3点讨论AGI进展",
    context={"user": "陈学东", "topic": "AGI", "type": "schedule"},
    importance=1.0
)

print(f"记忆已存储: {memory_id}")

# 检索记忆
results = ems.retrieve(
    query="陈博士的AGI会议",
    top_k=3
)

for result in results:
    print(f"匹配度: {result['match_score']:.2f}")
    print(f"内容: {result['content']}")
    print(f"Epiplexity: {result['epiplexity_score']:.2f}")
    print("---")

# 查看统计
stats = ems.get_stats()
print(f"总记忆数: {stats['total_memories']}")
print(f"平均Epiplexity: {stats['avg_epiplexity']:.2f}")

# 记忆巩固（睡眠模式）
ems.consolidate()
```

## 高级用法

### 自定义编码

```python
from ems.encoder import StructureEncoder

encoder = StructureEncoder(compute_budget=1e6)

encoded = encoder.encode(
    content="复杂的AGI研究内容...",
    context={"project": "EMS", "priority": "high"}
)

print(f"结构: {encoded['structure']}")
print(f"残差: {encoded['residual']}")
print(f"Epiplexity评分: {encoded['epiplexity_score']}")
```

### 分层检索

```python
from ems.retriever import HierarchicalRetriever

retriever = HierarchicalRetriever(compute_budget=1e6)

results = retriever.retrieve(
    query="AGI记忆系统",
    l1_memories=ems.l1_working,
    l2_memories=ems.l2_episodic,
    l3_memories=ems.l3_semantic,
    top_k=5
)
```

### 记忆巩固

```python
from ems.consolidator import MemoryConsolidator

consolidator = MemoryConsolidator()

consolidator.consolidate(
    l2_memories=ems.l2_episodic,
    l3_memories=ems.l3_semantic
)
```
