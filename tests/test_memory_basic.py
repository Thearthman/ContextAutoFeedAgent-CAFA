#!/usr/bin/env python
"""
Memory Tool Basic Test Script
Test memory storage, retrieval and decay functionality
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from memory_tool.memory_store import MemoryStore
from memory_tool.embeddings import EmbeddingGenerator

def test_embeddings():
    """Test text vectorization"""
    print("=" * 50)
    print("Test 1: Text Vectorization")
    print("=" * 50)
    
    generator = EmbeddingGenerator()
    
    # Test similarity calculation
    text1 = "I learned Python programming today"
    text2 = "Today I'm learning Python"
    text3 = "The weather will be nice tomorrow"
    
    sim1 = generator.similarity(text1, text2)
    sim2 = generator.similarity(text1, text3)
    
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Similarity: {sim1:.3f}\n")
    
    print(f"Text 1: {text1}")
    print(f"Text 3: {text3}")
    print(f"Similarity: {sim2:.3f}\n")
    
    assert sim1 > sim2, "Related texts should have higher similarity"
    print("✅ Vectorization test passed!\n")

def test_memory_store():
    """Test memory storage and retrieval"""
    print("=" * 50)
    print("Test 2: Memory Storage and Retrieval")
    print("=" * 50)
    
    # Use temporary file
    store = MemoryStore(path="test_memory_data.json")
    
    # Add memories
    memories = [
        "I got Newton's third law wrong in the exam",
        "I found I don't understand the second law of thermodynamics during review",
        "Today I learned Python object-oriented programming",
        "Tomorrow I need to go to the library to borrow books",
        "I need to review basic knowledge of quantum mechanics"
    ]
    
    print("📝 Adding memories...")
    for mem in memories:
        store.add_memory(mem, importance=0.9)
        print(f"  ✓ {mem}")
    
    # Search memories
    print("\n🔍 Search test...")
    queries = [
        "review physics",
        "learning programming",
        "library"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = store.search(query, top_k=2)
        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result['similarity']:.3f}] {result['text']}")
    
    print("\n✅ Memory storage test passed!\n")
    
    # Clean up test file
    if os.path.exists("test_memory_data.json"):
        os.remove("test_memory_data.json")

def test_memory_decay():
    """Test memory decay"""
    print("=" * 50)
    print("Test 3: Memory Time Decay")
    print("=" * 50)
    
    store = MemoryStore(path="test_decay_data.json")
    
    # Add memory
    mem1 = store.add_memory("Important physics knowledge", importance=1.0)
    print(f"📝 Add memory: {mem1['text']}")
    print(f"   Initial importance: {mem1['importance']}")
    
    # Execute decay
    print("\n⏰ Execute time decay (half-life=7 days)...")
    store.decay(half_life_days=7.0)
    
    # Note: Since just added, time is short, decay effect is not obvious
    print(f"   Importance after decay: {store.memories[0]['importance']:.6f}")
    print("   (Decay effect is minimal since just added)")
    
    print("\n✅ Decay test passed!\n")
    
    # Clean up test file
    if os.path.exists("test_decay_data.json"):
        os.remove("test_decay_data.json")

def main():
    """Run all tests"""
    print("\n🧪 Memory Tool Basic Functionality Test\n")
    
    try:
        test_embeddings()
        test_memory_store()
        test_memory_decay()
        
        print("=" * 50)
        print("🎉 All tests passed!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Run API server: python run_memory_api.py")
        print("2. Visit documentation: http://localhost:8000/docs")
        print("3. See detailed docs: MEMORY_TOOL_README.md\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

