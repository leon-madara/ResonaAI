#!/usr/bin/env python3
"""
Basic usage examples for ResonaAI Voice Emotion Detection Pipeline
"""

import requests
import json
import numpy as np
import soundfile as sf
import io
import asyncio
import websockets
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000/ws/emotion-stream"

def create_sample_audio(duration=2.0, frequency=440, sample_rate=16000):
    """Create sample audio for testing"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    return audio

def save_audio_to_bytes(audio, sample_rate=16000):
    """Save audio to bytes buffer"""
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format='WAV')
    buffer.seek(0)
    return buffer.getvalue()

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Health check passed: {data['status']}")
        print(f"   Message: {data['message']}")
        print(f"   Version: {data['version']}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_file_emotion_detection():
    """Test emotion detection from file upload"""
    print("\nTesting file emotion detection...")
    
    try:
        # Create sample audio
        audio = create_sample_audio(duration=2.0, frequency=440)
        audio_bytes = save_audio_to_bytes(audio)
        
        # Prepare file for upload
        files = {
            'file': ('test_audio.wav', audio_bytes, 'audio/wav')
        }
        
        # Make request
        response = requests.post(f"{API_BASE_URL}/detect-emotion/file", files=files)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ File emotion detection passed")
        print(f"   Detected emotion: {data['emotion']}")
        print(f"   Confidence: {data['confidence']:.3f}")
        print(f"   Processing time: {data.get('processing_time', 'N/A')}s")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ File emotion detection failed: {e}")
        return False

def test_batch_emotion_detection():
    """Test batch emotion detection"""
    print("\nTesting batch emotion detection...")
    
    try:
        # Create multiple sample audio files
        audio1 = create_sample_audio(duration=1.5, frequency=440)
        audio2 = create_sample_audio(duration=2.0, frequency=880)
        audio3 = create_sample_audio(duration=1.0, frequency=220)
        
        files = [
            ('files', ('audio1.wav', save_audio_to_bytes(audio1), 'audio/wav')),
            ('files', ('audio2.wav', save_audio_to_bytes(audio2), 'audio/wav')),
            ('files', ('audio3.wav', save_audio_to_bytes(audio3), 'audio/wav'))
        ]
        
        # Make request
        response = requests.post(f"{API_BASE_URL}/detect-emotion/batch", files=files)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Batch emotion detection passed")
        print(f"   Total files: {data['total_files']}")
        print(f"   Successful analyses: {data['successful_analyses']}")
        
        for i, result in enumerate(data['results']):
            if 'error' not in result:
                print(f"   File {i+1}: {result['emotion']} (confidence: {result['confidence']:.3f})")
            else:
                print(f"   File {i+1}: Error - {result['error']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Batch emotion detection failed: {e}")
        return False

def test_streaming_emotion_detection():
    """Test streaming emotion detection"""
    print("\nTesting streaming emotion detection...")
    
    try:
        # Create audio chunk
        audio_chunk = create_sample_audio(duration=0.1, frequency=440)
        audio_bytes = audio_chunk.astype(np.float32).tobytes()
        
        # Make request
        response = requests.post(f"{API_BASE_URL}/detect-emotion/stream", data=audio_bytes)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Streaming emotion detection passed")
        print(f"   Detected emotion: {data['emotion']}")
        print(f"   Confidence: {data['confidence']:.3f}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Streaming emotion detection failed: {e}")
        return False

async def test_websocket_emotion_stream():
    """Test WebSocket emotion streaming"""
    print("\nTesting WebSocket emotion streaming...")
    
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("   Connected to WebSocket")
            
            # Send multiple audio chunks
            for i in range(5):
                # Create audio chunk
                audio_chunk = create_sample_audio(duration=0.1, frequency=440 + i*100)
                audio_bytes = audio_chunk.astype(np.float32).tobytes()
                
                # Send audio data
                await websocket.send(audio_bytes)
                
                # Receive result
                result = await websocket.recv()
                data = json.loads(result)
                
                print(f"   Chunk {i+1}: {data['emotion']} (confidence: {data['confidence']:.3f})")
                
                # Small delay between chunks
                await asyncio.sleep(0.1)
            
            print("✅ WebSocket emotion streaming passed")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket emotion streaming failed: {e}")
        return False

def test_api_documentation():
    """Test API documentation endpoints"""
    print("\nTesting API documentation...")
    
    try:
        # Test OpenAPI docs
        response = requests.get(f"{API_BASE_URL}/docs")
        response.raise_for_status()
        print("✅ OpenAPI documentation accessible")
        
        # Test ReDoc
        response = requests.get(f"{API_BASE_URL}/redoc")
        response.raise_for_status()
        print("✅ ReDoc documentation accessible")
        
        # Test OpenAPI JSON
        response = requests.get(f"{API_BASE_URL}/openapi.json")
        response.raise_for_status()
        data = response.json()
        print(f"✅ OpenAPI JSON accessible (version: {data.get('info', {}).get('version', 'unknown')})")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API documentation test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("ResonaAI Voice Emotion Detection Pipeline - Basic Usage Examples")
    print("=" * 60)
    
    # Check if server is running
    if not test_health_check():
        print("\n❌ Server is not running. Please start the server first:")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Run all tests
    tests = [
        ("File Emotion Detection", test_file_emotion_detection),
        ("Batch Emotion Detection", test_batch_emotion_detection),
        ("Streaming Emotion Detection", test_streaming_emotion_detection),
        ("WebSocket Emotion Streaming", test_websocket_emotion_stream),
        ("API Documentation", test_api_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server logs for more details.")

if __name__ == "__main__":
    asyncio.run(main())
