#!/usr/bin/env python3
"""
Debug script to identify Gemma model issues.
"""

import torch
from transformers import AutoProcessor, Gemma3ForConditionalGeneration, BitsAndBytesConfig

def check_gpu_compatibility():
    """Check GPU compatibility with different dtypes."""
    print("🔍 GPU Compatibility Check")
    print("=" * 40)
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available - using CPU")
        return torch.float32
    
    gpu_props = torch.cuda.get_device_properties(0)
    print(f"GPU: {gpu_props.name}")
    print(f"Compute Capability: {gpu_props.major}.{gpu_props.minor}")
    print(f"Memory: {gpu_props.total_memory / 1e9:.1f} GB")
    
    # Test different dtypes
    dtypes_to_test = [torch.float32, torch.float16]
    if gpu_props.major >= 8:  # Ampere and newer
        dtypes_to_test.append(torch.bfloat16)
    
    working_dtypes = []
    for dtype in dtypes_to_test:
        try:
            test_tensor = torch.randn(100, 100, dtype=dtype, device='cuda')
            result = torch.matmul(test_tensor, test_tensor)
            working_dtypes.append(dtype)
            print(f"✅ {dtype} - Working")
        except Exception as e:
            print(f"❌ {dtype} - Failed: {e}")
    
    # Return best working dtype
    if torch.bfloat16 in working_dtypes:
        return torch.bfloat16
    elif torch.float16 in working_dtypes:
        return torch.float16
    else:
        return torch.float32

def test_model_loading():
    """Test different model loading configurations."""
    print("\n🔄 Testing Model Loading")
    print("=" * 40)
    
    model_id = "google/gemma-3-12b-it"
    best_dtype = check_gpu_compatibility()
    
    # Test configurations
    configs = [
        {
            "name": "8-bit quantized",
            "config": {
                "quantization_config": BitsAndBytesConfig(
                    load_in_8bit=True,
                    bnb_8bit_compute_dtype=best_dtype
                ),
                "torch_dtype": best_dtype,
                "device_map": "auto"
            }
        },
        {
            "name": "Standard loading",
            "config": {
                "torch_dtype": best_dtype,
                "device_map": "auto"
            }
        }
    ]
    
    for config in configs:
        try:
            print(f"\n🧪 Testing {config['name']}...")
            model = Gemma3ForConditionalGeneration.from_pretrained(
                model_id, **config['config']
            ).eval()
            
            processor = AutoProcessor.from_pretrained(model_id)
            
            print(f"✅ {config['name']} - Model loaded successfully")
            
            # Test basic generation
            test_generation(model, processor, config['name'])
            
            # Cleanup
            del model
            torch.cuda.empty_cache()
            return True
            
        except Exception as e:
            print(f"❌ {config['name']} - Failed: {e}")
    
    return False

def test_generation(model, processor, config_name):
    """Test text generation with different parameters."""
    print(f"🎯 Testing generation with {config_name}...")
    
    messages = [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]}
    ]
    
    # Test parameters from conservative to aggressive
    test_params = [
        {
            "name": "Greedy (safest)",
            "params": {
                "max_new_tokens": 20,
                "do_sample": False,
            }
        },
        {
            "name": "Conservative sampling",
            "params": {
                "max_new_tokens": 20,
                "do_sample": True,
                "temperature": 1.0,
                "top_p": 0.95,
                "top_k": 50,
            }
        },
        {
            "name": "Your original settings",
            "params": {
                "max_new_tokens": 50,
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }
    ]
    
    for test in test_params:
        try:
            inputs = processor.apply_chat_template(
                messages, add_generation_prompt=True, tokenize=True,
                return_dict=True, return_tensors="pt"
            ).to(model.device)
            
            with torch.inference_mode():
                outputs = model.generate(
                    **inputs,
                    pad_token_id=processor.tokenizer.eos_token_id,
                    **test['params']
                )
            
            # Decode response
            input_len = inputs["input_ids"].shape[-1]
            response = processor.decode(outputs[0][input_len:], skip_special_tokens=True)
            
            print(f"   ✅ {test['name']}: {response[:50]}...")
            
        except Exception as e:
            print(f"   ❌ {test['name']}: {e}")

def main():
    print("🚀 Gemma Model Debug Tool")
    print("=" * 50)
    
    try:
        success = test_model_loading()
        if success:
            print("\n🎉 At least one configuration worked!")
            print("Use the successful configuration in your chat script.")
        else:
            print("\n😞 All configurations failed.")
            print("Consider using a smaller model or different hardware.")
            
    except KeyboardInterrupt:
        print("\n🛑 Debug interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()
