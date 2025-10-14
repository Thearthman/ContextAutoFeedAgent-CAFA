#!/usr/bin/env python3
"""
增强版记忆存储系统
集成智能权重评估和自适应衰减
"""

import os
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from .embeddings import EmbeddingGenerator
from .smart_weight import SmartWeightEvaluator, AdaptiveDecay


class EnhancedMemoryStore:
    """
    增强版记忆存储系统
    功能：
    - 智能权重评估
    - 自适应衰减（高权重衰减慢）
    - 用户提醒机制
    - 记忆重要性追踪
    """
    
    def __init__(self, path: str = "enhanced_memory_data.json"):
        self.path = path
        self.model = EmbeddingGenerator()
        self.weight_evaluator = SmartWeightEvaluator()
        self.memories = self._load()
        
        # Statistics信息
        self.stats = {
            "total_memories": len(self.memories),
            "high_importance_count": 0,
            "auto_weight_adjustments": 0,
            "user_prompted_count": 0
        }
        self._update_stats()
    
    def _load(self) -> List[Dict]:
        """加载记忆数据"""
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save(self):
        """保存记忆数据"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)
    
    def _update_stats(self):
        """Update统计信息"""
        self.stats["total_memories"] = len(self.memories)
        self.stats["high_importance_count"] = sum(
            1 for m in self.memories if m["importance"] >= 0.8
        )
    
    def add_memory(
        self,
        text: str,
        importance: Optional[float] = None,
        context: Optional[Dict] = None,
        auto_evaluate: bool = True,
        tags: List[str] = None
    ) -> Dict:
        """
        添加记忆（增强版）
        
        Args:
            text: 记忆内容
            importance: 手动指定的重要性（如果为 None，则自动评估）
            context: 额外上下文信息
            auto_evaluate: 是否自动评估权重
            tags: 记忆标签
        
        Returns:
            记忆对象（包含评估信息）
        """
        # 1. 智能权重评估
        if importance is None and auto_evaluate:
            auto_importance, reasons = self.weight_evaluator.evaluate_weight(text, context)
            importance = auto_importance
            evaluation_info = {
                "auto_evaluated": True,
                "evaluation_reasons": reasons,
                "evaluated_at": datetime.now().isoformat()
            }
        else:
            if importance is None:
                importance = 0.5  # 默认值
            evaluation_info = {
                "auto_evaluated": False,
                "manual_weight": True
            }
        
        # 2. 检查是否需要提醒用户
        should_prompt, prompt_message = self.weight_evaluator.should_prompt_user(text, importance)
        
        # 3. 获取权重分类和衰减信息
        category, description = self.weight_evaluator.get_weight_category(importance)
        decay_info = AdaptiveDecay.get_decay_info(importance)
        
        # 4. 生成向量嵌入
        embedding = self.model.embed(text).tolist()
        
        # 5. 创建记忆对象
        memory = {
            "text": text,
            "embedding": embedding,
            "importance": importance,
            "original_importance": importance,  # 保存原始权重
            "timestamp": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "access_count": 0,
            "category": category,
            "half_life_days": decay_info["half_life_days"],
            "evaluation_info": evaluation_info,
            "tags": tags or [],
            "metadata": {
                "should_prompt_user": should_prompt,
                "prompt_message": prompt_message if should_prompt else None,
                "decay_rate": decay_info["decay_rate"]
            }
        }
        
        self.memories.append(memory)
        self._save()
        self._update_stats()
        
        # 如果需要提醒用户，记录统计
        if should_prompt:
            self.stats["user_prompted_count"] += 1
        
        return memory
    
    def search(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.3,
        importance_boost: bool = True
    ) -> List[Dict]:
        """
        搜索记忆（增强版）
        
        Args:
            query: 查询文本
            top_k: 返回前 K 个结果
            min_similarity: 最小相似度阈值
            importance_boost: 是否根据重要性加权
        
        Returns:
            匹配的记忆列表
        """
        if not self.memories:
            return []
        
        query_vec = self.model.embed(query)
        scores = []
        
        for mem in self.memories:
            emb = np.array(mem["embedding"])
            
            # 计算余弦相似度
            sim = np.dot(query_vec, emb) / (np.linalg.norm(query_vec) * np.linalg.norm(emb))
            
            # 如果启用重要性加权，调整相似度分数
            if importance_boost:
                # 重要性权重 (importance) 会提升相似度
                # 例如：importance=0.9 的记忆相似度会被轻微提升
                boosted_sim = sim * (1 + mem["importance"] * 0.2)
            else:
                boosted_sim = sim
            
            # 过滤低相似度结果
            if sim >= min_similarity:
                scores.append((mem, float(sim), float(boosted_sim)))
                
                # Update访问统计
                mem["last_accessed"] = datetime.now().isoformat()
                mem["access_count"] += 1
        
        # 按加权后的相似度排序
        results = sorted(scores, key=lambda x: x[2], reverse=True)[:top_k]
        
        # 保存更新后的访问统计
        if results:
            self._save()
        
        return [{
            "text": m["text"],
            "similarity": round(sim, 3),
            "importance": m["importance"],
            "category": m["category"],
            "access_count": m["access_count"],
            "tags": m.get("tags", [])
        } for m, sim, _ in results]
    
    def adaptive_decay(self):
        """
        自适应衰减 - 根据每个记忆的重要性使用不同的衰减速度
        """
        now = datetime.now()
        updated_count = 0
        
        for mem in self.memories:
            t = datetime.fromisoformat(mem["timestamp"])
            days_passed = (now - t).days
            
            if days_passed <= 0:
                continue  # 今天的记忆不衰减
            
            # 使用自适应衰减
            original_importance = mem.get("original_importance", mem["importance"])
            new_importance = AdaptiveDecay.calculate_decay(
                original_importance,
                days_passed
            )
            
            # Update重要性
            if mem["importance"] != new_importance:
                mem["importance"] = new_importance
                updated_count += 1
                
                # Update分类
                category, _ = self.weight_evaluator.get_weight_category(new_importance)
                mem["category"] = category
        
        self._save()
        self._update_stats()
        
        return {
            "updated_count": updated_count,
            "total_memories": len(self.memories),
            "high_importance_remaining": self.stats["high_importance_count"]
        }
    
    def update_importance(self, memory_index: int, new_importance: float) -> bool:
        """
        手动更新记忆的重要性
        
        Args:
            memory_index: 记忆索引
            new_importance: 新的重要性值
        
        Returns:
            是否成功
        """
        if 0 <= memory_index < len(self.memories):
            mem = self.memories[memory_index]
            mem["importance"] = new_importance
            mem["original_importance"] = new_importance  # Update原始权重
            
            # Update分类和衰减信息
            category, _ = self.weight_evaluator.get_weight_category(new_importance)
            decay_info = AdaptiveDecay.get_decay_info(new_importance)
            
            mem["category"] = category
            mem["half_life_days"] = decay_info["half_life_days"]
            mem["metadata"]["decay_rate"] = decay_info["decay_rate"]
            
            self._save()
            self._update_stats()
            self.stats["auto_weight_adjustments"] += 1
            
            return True
        return False
    
    def get_memories_by_category(self, category: str) -> List[Dict]:
        """按分类获取记忆"""
        return [m for m in self.memories if m.get("category") == category]
    
    def get_memories_needing_review(self, days_threshold: int = 30) -> List[Dict]:
        """Get需要复习的记忆"""
        now = datetime.now()
        review_needed = []
        
        for mem in self.memories:
            last_accessed = datetime.fromisoformat(mem.get("last_accessed", mem["timestamp"]))
            days_since_access = (now - last_accessed).days
            
            # 重要记忆长时间未访问，需要复习
            if mem["importance"] >= 0.7 and days_since_access >= days_threshold:
                review_needed.append({
                    "text": mem["text"],
                    "importance": mem["importance"],
                    "days_since_access": days_since_access,
                    "access_count": mem["access_count"]
                })
        
        return sorted(review_needed, key=lambda x: x["importance"], reverse=True)
    
    def get_stats(self) -> Dict:
        """Get统计信息"""
        return {
            **self.stats,
            "categories": {
                "永久记忆": len(self.get_memories_by_category("永久记忆")),
                "重要记忆": len(self.get_memories_by_category("重要记忆")),
                "常规记忆": len(self.get_memories_by_category("常规记忆")),
                "临时记忆": len(self.get_memories_by_category("临时记忆")),
            },
            "avg_importance": np.mean([m["importance"] for m in self.memories]) if self.memories else 0
        }


# 使用示例
if __name__ == "__main__":
    print("🧠 增强版记忆存储系统测试")
    print("=" * 70)
    
    store = EnhancedMemoryStore(path="test_enhanced_memory.json")
    
    # Test添加记忆
    test_memories = [
        "记住，我的 API Key 是 sk-1234567890",
        "我在开发一个 AI 助手项目",
        "今天天气不错",
        "我喜欢使用 Python 编程",
    ]
    
    print("\n1️⃣ 添加记忆:")
    for text in test_memories:
        memory = store.add_memory(text)
        print(f"\n📝 {text}")
        print(f"   权重: {memory['importance']:.2f} ({memory['category']})")
        print(f"   衰减速度: {memory['metadata']['decay_rate']}")
        print(f"   半衰期: {memory['half_life_days']} 天")
        
        if memory['metadata']['should_prompt_user']:
            print(f"   💡 {memory['metadata']['prompt_message']}")
    
    # Test搜索
    print("\n2️⃣ 搜索记忆:")
    results = store.search("编程", top_k=3)
    for r in results:
        print(f"   [{r['similarity']:.3f}] {r['text']} (权重: {r['importance']:.2f})")
    
    # Test自适应衰减
    print("\n3️⃣ 自适应衰减:")
    decay_result = store.adaptive_decay()
    print(f"   更新了 {decay_result['updated_count']} 条记忆")
    print(f"   剩余高重要性记忆: {decay_result['high_importance_remaining']} 条")
    
    # Statistics信息
    print("\n4️⃣ 统计信息:")
    stats = store.get_stats()
    print(f"   总记忆数: {stats['total_memories']}")
    print(f"   高重要性记忆: {stats['high_importance_count']}")
    print(f"   平均重要性: {stats['avg_importance']:.2f}")
    print(f"   分类统计: {stats['categories']}")
    
    # Clean up测试文件
    if os.path.exists("test_enhanced_memory.json"):
        os.remove("test_enhanced_memory.json")
