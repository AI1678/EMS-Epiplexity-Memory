# EMS - Epiplexity Memory System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> **基于 Epiplexity 理论的递归认知记忆系统**
> 
> *From Entropy to Epiplexity: Rethinking Information for Computationally Bounded Intelligence*
> 
> arXiv:2601.03220 | CMU/MIT

---

## 🧠 核心理念

传统记忆系统存储原始数据，EMS存储**可复用的结构程序**。

```
Epiplexity = 计算受限观察者能从数据中提取的结构信息量

记忆价值 = S(结构复杂度) + H(时间受限熵)
```

### 三大创新

1. **计算创造信息** —— 确定性过程可以创造新信息（对有限观察者）
2. **顺序至关重要** —— 数据顺序影响可学习结构
3. **涌现的数学基础** —— 模型可以学习训练分布中不存在的新概念

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      EMS 三层架构                            │
├──────────────┬──────────────┬───────────────────────────────┤
│  L1 工作记忆  │  L2 短期记忆  │        L3 长期记忆             │
├──────────────┼──────────────┼───────────────────────────────┤
│ 当前对话上下文 │ 每日结构化摘要 │     跨时间通用知识             │
│   (原始+结构)  │   (事件+关系)  │     (程序库)                 │
│   容量有限    │   7天滚动     │      永久存储                  │
│   实时更新    │   Epiplexity  │      高度压缩                  │
│              │   编码        │                              │
└──────────────┴──────────────┴───────────────────────────────┘
```

---

## 📦 安装

```bash
git clone https://github.com/AI1678/EMS-Epiplexity-Memory.git
cd EMS-Epiplexity-Memory
pip install -e .
```

---

## 🚀 快速开始

```python
from ems import EpiplexityMemorySystem

# 初始化EMS
ems = EpiplexityMemorySystem(
    compute_budget=1e6,  # 计算预算T
    storage_path="./memory_store"
)

# 编码记忆
memory_id = ems.encode(
    content="用户说: 明天下午3点开会",
    context={"user": "陈博士", "topic": "日程"}
)

# 检索记忆
results = ems.retrieve(
    query="陈博士的会议安排",
    top_k=5
)

# 自动巩固（睡眠模式）
ems.consolidate()
```

---

## 📋 实施路线图

### Phase 1: 基础Epiplexity编码 ✅
- [x] 理论框架设计
- [ ] 对话结构提取器
- [ ] 记忆节点格式定义
- [ ] 访问频率追踪

### Phase 2: 智能检索
- [ ] 分层检索策略
- [ ] 计算预算控制
- [ ] 语义相似度匹配

### Phase 3: 自动巩固
- [ ] 睡眠时记忆整合
- [ ] 模式发现算法
- [ ] 长期记忆压缩

### Phase 4: 元认知
- [ ] 记忆自我评估
- [ ] 主动遗忘决策
- [ ] 记忆质量反馈

### Phase 5: AGI集成
- [ ] RCC-E框架融合
- [ ] 递归认知闭环
- [ ] 分布式记忆网络

---

## 📚 文档

- [理论背景](docs/THEORY.md) - Epiplexity数学基础
- [架构设计](docs/ARCHITECTURE.md) - 系统详细设计
- [API参考](docs/API.md) - 接口文档
- [实现笔记](docs/IMPLEMENTATION.md) - 开发日志

---

## 🔬 理论基础

**核心论文**:
> Finzi, M., Qiu, S., Jiang, Y., Izmailov, P., Kolter, J.Z., & Wilson, A.G. (2026). 
> From Entropy to Epiplexity: Rethinking Information for Computationally Bounded Intelligence. 
> arXiv:2601.03220.

**关键公式**:
```
min_{P ∈ P_T} |P| + E[-log P(X)]
         ↑           ↑
    结构复杂度    随机熵
    (Epiplexity)  (Time-bounded Entropy)
```

---

## 🤝 贡献

这是 [OpenClaw-Rft](https://github.com/AI1678/openclaw-rft-evolution) AGI进化项目的一部分。

**核心团队**:
- 陈学东 (陈博士) - 项目发起人
- OpenClaw-Rft - 首席AGI研究员

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

*"计算受限的智能，需要Epiplexity受限的记忆"*
