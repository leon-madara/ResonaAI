#!/usr/bin/env python3
"""
Advanced usage examples for ResonaAI Voice Emotion Detection Pipeline
"""

import requests
import json
import numpy as np
import soundfile as sf
import io
import asyncio
import websockets
import time
from pathlib import Path
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns

# API Configuration
API_BASE_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000/ws/emotion-stream"

class EmotionAnalyzer:
    """Advanced emotion analysis client"""
    
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.session = requests.Session()
    
    def analyze_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze emotion from audio file"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f.read(), 'audio/wav')}
                response = self.session.post(f"{self.api_url}/detect-emotion/file", files=files)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_audio_batch(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze emotions from multiple audio files"""
        try:
            files = []
            for file_path in file_paths:
                with open(file_path, 'rb') as f:
                    files.append(('files', (Path(file_path).name, f.read(), 'audio/wav')))
            
            response = self.session.post(f"{self.api_url}/detect-emotion/batch", files=files)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_audio_stream(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze emotion from audio stream"""
        try:
            response = self.session.post(f"{self.api_url}/detect-emotion/stream", data=audio_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

class RealTimeEmotionMonitor:
    """Real-time emotion monitoring using WebSocket"""
    
    def __init__(self, websocket_url: str = WEBSOCKET_URL):
        self.websocket_url = websocket_url
        self.emotion_history = []
        self.confidence_history = []
        self.timestamps = []
    
    async def start_monitoring(self, duration: int = 30):
        """Start real-time emotion monitoring"""
        print(f"Starting real-time emotion monitoring for {duration} seconds...")
        
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    # Generate sample audio chunk
                    audio_chunk = self._generate_audio_chunk()
                    audio_bytes = audio_chunk.astype(np.float32).tobytes()
                    
                    # Send audio data
                    await websocket.send(audio_bytes)
                    
                    # Receive result
                    result = await websocket.recv()
                    data = json.loads(result)
                    
                    # Store results
                    self.emotion_history.append(data['emotion'])
                    self.confidence_history.append(data['confidence'])
                    self.timestamps.append(time.time())
                    
                    # Print current result
                    print(f"Time: {time.time() - start_time:.1f}s - "
                          f"Emotion: {data['emotion']} - "
                          f"Confidence: {data['confidence']:.3f}")
                    
                    await asyncio.sleep(0.1)  # 100ms intervals
                
                print("Monitoring completed!")
                return True
                
        except Exception as e:
            print(f"Monitoring failed: {e}")
            return False
    
    def _generate_audio_chunk(self) -> np.ndarray:
        """Generate sample audio chunk"""
        # Simulate different emotional states with different frequencies
        emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'neutral']
        current_emotion = np.random.choice(emotions)
        
        # Map emotions to frequencies
        emotion_freqs = {
            'happy': 440,    # A4
            'sad': 220,      # A3
            'angry': 880,    # A5
            'fear': 330,     # E4
            'surprise': 660, # E5
            'neutral': 440   # A4
        }
        
        frequency = emotion_freqs[current_emotion]
        duration = 0.1  # 100ms
        sample_rate = 16000
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Add some noise
        audio += 0.05 * np.random.randn(len(audio))
        
        return audio
    
    def plot_emotion_timeline(self):
        """Plot emotion timeline"""
        if not self.emotion_history:
            print("No emotion data to plot")
            return
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot emotion timeline
        emotions = ['neutral', 'happy', 'sad', 'angry', 'fear', 'surprise', 'disgust']
        emotion_colors = {
            'neutral': 'gray',
            'happy': 'yellow',
            'sad': 'blue',
            'angry': 'red',
            'fear': 'purple',
            'surprise': 'orange',
            'disgust': 'green'
        }
        
        # Convert emotions to numeric values for plotting
        emotion_numeric = [emotions.index(emotion) if emotion in emotions else 0 
                          for emotion in self.emotion_history]
        
        times = [t - self.timestamps[0] for t in self.timestamps]
        
        ax1.plot(times, emotion_numeric, 'o-', markersize=4)
        ax1.set_yticks(range(len(emotions)))
        ax1.set_yticklabels(emotions)
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Emotion')
        ax1.set_title('Emotion Timeline')
        ax1.grid(True, alpha=0.3)
        
        # Plot confidence timeline
        ax2.plot(times, self.confidence_history, 'o-', color='green', markersize=4)
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Confidence')
        ax2.set_title('Confidence Timeline')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1)
        
        plt.tight_layout()
        plt.show()
    
    def get_emotion_statistics(self) -> Dict[str, Any]:
        """Get emotion statistics"""
        if not self.emotion_history:
            return {}
        
        # Count emotions
        emotion_counts = {}
        for emotion in self.emotion_history:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Calculate statistics
        total_samples = len(self.emotion_history)
        avg_confidence = np.mean(self.confidence_history)
        max_confidence = np.max(self.confidence_history)
        min_confidence = np.min(self.confidence_history)
        
        # Most common emotion
        most_common_emotion = max(emotion_counts, key=emotion_counts.get)
        
        return {
            'total_samples': total_samples,
            'emotion_counts': emotion_counts,
            'emotion_percentages': {emotion: count/total_samples*100 
                                  for emotion, count in emotion_counts.items()},
            'most_common_emotion': most_common_emotion,
            'average_confidence': avg_confidence,
            'max_confidence': max_confidence,
            'min_confidence': min_confidence,
            'duration_seconds': self.timestamps[-1] - self.timestamps[0] if self.timestamps else 0
        }

def create_emotion_dataset():
    """Create a dataset of different emotional audio samples"""
    print("Creating emotion dataset...")
    
    # Define emotional characteristics
    emotions = {
        'happy': {'freq': 440, 'amplitude': 0.5, 'duration': 2.0},
        'sad': {'freq': 220, 'amplitude': 0.3, 'duration': 2.0},
        'angry': {'freq': 880, 'amplitude': 0.7, 'duration': 2.0},
        'fear': {'freq': 330, 'amplitude': 0.4, 'duration': 2.0},
        'surprise': {'freq': 660, 'amplitude': 0.6, 'duration': 2.0},
        'neutral': {'freq': 440, 'amplitude': 0.4, 'duration': 2.0}
    }
    
    dataset = []
    
    for emotion, params in emotions.items():
        # Create audio
        t = np.linspace(0, params['duration'], int(16000 * params['duration']))
        audio = params['amplitude'] * np.sin(2 * np.pi * params['freq'] * t)
        
        # Add some variation
        audio += 0.1 * np.random.randn(len(audio))
        
        # Save to bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio, 16000, format='WAV')
        audio_bytes = buffer.getvalue()
        
        dataset.append({
            'emotion': emotion,
            'audio': audio_bytes,
            'filename': f'{emotion}_sample.wav'
        })
    
    print(f"Created dataset with {len(dataset)} samples")
    return dataset

async def advanced_emotion_analysis():
    """Perform advanced emotion analysis"""
    print("ResonaAI Advanced Emotion Analysis")
    print("=" * 40)
    
    # Check server health
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please start the server first.")
        return
    
    # Create emotion analyzer
    analyzer = EmotionAnalyzer()
    
    # Create dataset
    dataset = create_emotion_dataset()
    
    # Analyze each sample
    print("\nAnalyzing emotion dataset...")
    results = []
    
    for sample in dataset:
        result = analyzer.analyze_audio_stream(sample['audio'])
        if 'error' not in result:
            results.append({
                'expected': sample['emotion'],
                'predicted': result['emotion'],
                'confidence': result['confidence']
            })
            print(f"Expected: {sample['emotion']:8} | "
                  f"Predicted: {result['emotion']:8} | "
                  f"Confidence: {result['confidence']:.3f}")
        else:
            print(f"Error analyzing {sample['emotion']}: {result['error']}")
    
    # Calculate accuracy
    if results:
        correct = sum(1 for r in results if r['expected'] == r['predicted'])
        accuracy = correct / len(results) * 100
        avg_confidence = np.mean([r['confidence'] for r in results])
        
        print(f"\nAnalysis Results:")
        print(f"Accuracy: {accuracy:.1f}% ({correct}/{len(results)})")
        print(f"Average Confidence: {avg_confidence:.3f}")
    
    # Real-time monitoring
    print("\nStarting real-time emotion monitoring...")
    monitor = RealTimeEmotionMonitor()
    
    if await monitor.start_monitoring(duration=10):
        # Get statistics
        stats = monitor.get_emotion_statistics()
        print(f"\nMonitoring Statistics:")
        print(f"Total samples: {stats['total_samples']}")
        print(f"Most common emotion: {stats['most_common_emotion']}")
        print(f"Average confidence: {stats['average_confidence']:.3f}")
        print(f"Duration: {stats['duration_seconds']:.1f} seconds")
        
        # Plot results
        try:
            monitor.plot_emotion_timeline()
        except Exception as e:
            print(f"Could not plot results: {e}")

def performance_benchmark():
    """Run performance benchmark"""
    print("Running performance benchmark...")
    
    analyzer = EmotionAnalyzer()
    
    # Create test audio
    audio = np.random.randn(16000 * 2)  # 2 seconds
    audio_bytes = audio.astype(np.float32).tobytes()
    
    # Benchmark streaming detection
    times = []
    for i in range(10):
        start_time = time.time()
        result = analyzer.analyze_audio_stream(audio_bytes)
        end_time = time.time()
        
        if 'error' not in result:
            times.append(end_time - start_time)
    
    if times:
        avg_time = np.mean(times)
        min_time = np.min(times)
        max_time = np.max(times)
        
        print(f"Performance Results:")
        print(f"Average processing time: {avg_time:.3f}s")
        print(f"Minimum processing time: {min_time:.3f}s")
        print(f"Maximum processing time: {max_time:.3f}s")
        print(f"Throughput: {1/avg_time:.1f} requests/second")

async def main():
    """Main function"""
    await advanced_emotion_analysis()
    performance_benchmark()

if __name__ == "__main__":
    asyncio.run(main())
