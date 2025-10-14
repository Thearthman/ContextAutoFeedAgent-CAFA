#!/usr/bin/env python3
"""
Intelligent Memory Weight Evaluation System
Automatically analyze content importance and suggest appropriate weights
"""

import re
from typing import Dict, Tuple, List
from datetime import datetime


class SmartWeightEvaluator:
    """Intelligent weight evaluator"""
    
    def __init__(self):
        # High importance keywords (weight +0.3)
        self.high_importance_keywords = [
            "remember", "important", "critical", "must", "definitely", "absolutely",
            "password", "account", "API", "secret", "private",
            "birthday", "phone", "address", "ID",
            "goal", "plan", "deadline", "due date",
            "don't forget", "remind me", "make sure"
        ]
        
        # Medium importance keywords (weight +0.15)
        self.medium_importance_keywords = [
            "like", "dislike", "prefer", "habit",
            "project", "work", "study", "research",
            "want", "need", "hope", "intend",
            "problem", "error", "bug", "issue"
        ]
        
        # Factual information patterns (weight +0.2)
        self.factual_patterns = [
            r"my .* is",
            r"I work at",
            r"I use",
            r"I am .*ing",
            r"\d{4}-\d{1,2}-\d{1,2}",  # Date
            r"[A-Z]{2,}[- ]?\d+",  # Model/code
        ]
        
        # Low value content (weight -0.2)
        self.low_value_patterns = [
            r"^(hi|hello|hey)$",
            r"^(thank you|thanks)$",
            r"^(bye|goodbye)$",
            r"^(yes|ok|okay)$",
        ]
    
    def evaluate_weight(self, text: str, context: Dict = None) -> Tuple[float, List[str]]:
        """
        Evaluate content weight
        
        Args:
            text: Text to evaluate
            context: Additional context information (e.g., conversation history, user intent, etc.)
        
        Returns:
            (weight value, reason list)
        """
        base_weight = 0.5  # Base weight
        reasons = []
        
        # 1. Check high importance keywords
        for keyword in self.high_importance_keywords:
            if keyword in text:
                base_weight += 0.3
                reasons.append(f"Contains high importance keyword: '{keyword}'")
                break  # Add only once
        
        # 2. Check medium importance keywords
        for keyword in self.medium_importance_keywords:
            if keyword in text:
                base_weight += 0.15
                reasons.append(f"Contains medium importance keyword: '{keyword}'")
                break
        
        # 3. 检查事实性信息
        for pattern in self.factual_patterns:
            if re.search(pattern, text):
                base_weight += 0.2
                reasons.append(f"包含事实性信息")
                break
        
        # 4. 文本长度评估
        if len(text) > 100:
            base_weight += 0.1
            reasons.append("内容较长，可能包含重要信息")
        elif len(text) < 10:
            base_weight -= 0.15
            reasons.append("内容过短")
        
        # 5. 检查低价值内容
        for pattern in self.low_value_patterns:
            if re.match(pattern, text.strip(), re.IGNORECASE):
                base_weight -= 0.2
                reasons.append("检测到低价值内容（简单问候语）")
                break
        
        # 6. 上下文分析
        if context:
            if context.get("user_explicit_save"):
                base_weight += 0.2
                reasons.append("用户明确要求保存")
            
            if context.get("conversation_importance"):
                base_weight += 0.15
                reasons.append("对话被标记为重要")
        
        # 7. 个人信息检测（高权重）
        personal_info_patterns = [
            r"我叫|我的名字",
            r"我在.*(公司|学校|大学)",
            r"我的(电话|手机|邮箱|email)",
        ]
        for pattern in personal_info_patterns:
            if re.search(pattern, text):
                base_weight += 0.25
                reasons.append("包含个人信息")
                break
        
        # 确保权重在 0-1 之间
        final_weight = max(0.0, min(1.0, base_weight))
        
        return final_weight, reasons
    
    def should_prompt_user(self, text: str, auto_weight: float) -> Tuple[bool, str]:
        """
        判断是否应该提示用户调整权重
        
        Args:
            text: 文本内容
            auto_weight: 自动评估的权重
        
        Returns:
            (是否提示, 提示消息)
        """
        # 如果自动权重很高（>0.8），但可能还有提升空间
        if auto_weight >= 0.8:
            return True, f"检测到高价值内容（权重: {auto_weight:.2f}），是否需要设为永久保存？"
        
        # 如果包含"记住"等明确指令，但权重不是最高
        explicit_keywords = ["记住", "记得", "不要忘记", "别忘了"]
        if any(kw in text for kw in explicit_keywords) and auto_weight < 0.95:
            return True, f"检测到明确保存指令，建议提高权重至 0.95+"
        
        # 如果权重中等（0.5-0.7），询问是否重要
        if 0.5 <= auto_weight <= 0.7:
            return True, f"内容权重为 {auto_weight:.2f}，这个信息对你重要吗？"
        
        return False, ""
    
    def get_weight_category(self, weight: float) -> Tuple[str, str]:
        """
        获取权重分类和描述
        
        Returns:
            (分类名称, 描述)
        """
        if weight >= 0.9:
            return "永久记忆", "几乎不会衰减，长期保存"
        elif weight >= 0.75:
            return "重要记忆", "衰减缓慢，重点保留"
        elif weight >= 0.5:
            return "常规记忆", "正常衰减，定期复习"
        elif weight >= 0.3:
            return "临时记忆", "快速衰减，短期有效"
        else:
            return "低优先级", "快速遗忘，不重要"


class AdaptiveDecay:
    """自适应衰减系统 - 根据权重调整衰减速度"""
    
    @staticmethod
    def get_half_life(importance: float) -> float:
        """
        根据重要性获取半衰期（天数）
        重要性越高，半衰期越长（衰减越慢）
        
        Args:
            importance: 重要性权重 (0-1)
        
        Returns:
            半衰期天数
        """
        if importance >= 0.9:
            return 365  # 1年 - 永久记忆
        elif importance >= 0.75:
            return 90   # 3个月 - 重要记忆
        elif importance >= 0.5:
            return 30   # 1个月 - 常规记忆
        elif importance >= 0.3:
            return 7    # 1周 - 临时记忆
        else:
            return 3    # 3天 - 低优先级
    
    @staticmethod
    def calculate_decay(
        original_importance: float,
        days_passed: float,
        custom_half_life: float = None
    ) -> float:
        """
        计算衰减后的重要性
        
        Args:
            original_importance: 原始重要性
            days_passed: 经过的天数
            custom_half_life: 自定义半衰期（如果不提供，根据重要性自动计算）
        
        Returns:
            衰减后的重要性
        """
        if custom_half_life is None:
            half_life = AdaptiveDecay.get_half_life(original_importance)
        else:
            half_life = custom_half_life
        
        # 指数衰减公式
        decay_factor = 0.5 ** (days_passed / half_life)
        new_importance = original_importance * decay_factor
        
        return new_importance
    
    @staticmethod
    def get_decay_info(importance: float) -> Dict:
        """
        获取衰减信息
        
        Returns:
            包含衰减参数的字典
        """
        half_life = AdaptiveDecay.get_half_life(importance)
        
        # 计算不同时间点的重要性
        decay_timeline = {
            "1天后": AdaptiveDecay.calculate_decay(importance, 1, half_life),
            "1周后": AdaptiveDecay.calculate_decay(importance, 7, half_life),
            "1个月后": AdaptiveDecay.calculate_decay(importance, 30, half_life),
            "3个月后": AdaptiveDecay.calculate_decay(importance, 90, half_life),
            "1年后": AdaptiveDecay.calculate_decay(importance, 365, half_life),
        }
        
        return {
            "half_life_days": half_life,
            "decay_timeline": decay_timeline,
            "decay_rate": "缓慢" if half_life >= 90 else "中等" if half_life >= 30 else "快速"
        }


# 使用示例
if __name__ == "__main__":
    evaluator = SmartWeightEvaluator()
    
    test_cases = [
        "你好",
        "今天天气不错",
        "记住，我的生日是 10 月 15 日",
        "我的 API Key 是 sk-1234567890",
        "我在开发一个 AI 助手项目",
        "我喜欢使用 Python 编程",
        "我的 GPU 是 NVIDIA RTX 4070",
    ]
    
    print("🧠 智能权重评估系统测试")
    print("=" * 70)
    
    for text in test_cases:
        weight, reasons = evaluator.evaluate_weight(text)
        should_prompt, prompt_msg = evaluator.should_prompt_user(text, weight)
        category, desc = evaluator.get_weight_category(weight)
        decay_info = AdaptiveDecay.get_decay_info(weight)
        
        print(f"\n📝 文本: {text}")
        print(f"⚖️  权重: {weight:.2f} ({category})")
        print(f"📊 衰减速度: {decay_info['decay_rate']} (半衰期: {decay_info['half_life_days']} 天)")
        
        if reasons:
            print(f"📌 评估原因:")
            for reason in reasons:
                print(f"   • {reason}")
        
        if should_prompt:
            print(f"💡 提示: {prompt_msg}")
        
        print(f"\n⏰ 衰减预测:")
        for time_point, value in decay_info['decay_timeline'].items():
            print(f"   {time_point}: {value:.3f}")

