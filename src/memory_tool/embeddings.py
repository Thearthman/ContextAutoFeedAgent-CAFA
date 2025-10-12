# memory_tool/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    """
    A simple embedding generator using SentenceTransformer.
    用于生成文本语义向量的类。
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # 加载轻量级向量模型
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> np.ndarray:
        """
        将文本转换为向量。
        """
        if not text.strip():
            raise ValueError("输入文本不能为空")
        embedding = self.model.encode(text)
        return np.array(embedding)

    def similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的语义相似度（余弦相似度）。
        """
        emb1 = self.embed(text1)
        emb2 = self.embed(text2)
        sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(sim)


# 测试
if __name__ == "__main__":
    generator = EmbeddingGenerator()
    sim = generator.similarity("你好，今天过得怎么样？", "今天天气不错，你好吗？")
    print(f"相似度: {sim:.3f}")

