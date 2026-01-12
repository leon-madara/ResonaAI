"""
Demo Script for MockAPIServer

This script demonstrates how to use the MockAPIServer with generated test data.
"""

import asyncio
import time
from pathlib import Path

from ..api.mock_api_server import MockAPIServer
from ..storage.local_storage import LocalStorageManager
from ..models import ServiceConfig


async def run_api_server_demo():
    """Run a demonstration of the MockAPIServer"""
    print("🚀 Starting MockAPIServer Demo")
    
    # Setup storage with demo data directory
    demo_data_path = Path("demo_data")
    storage = LocalStorageManager(str(demo_data_path))
    
    # Create mock API server
    api_server = MockAPIServer(storage)
    
    # Configure server
    config = ServiceConfig(
        mock_api_port=8001,
        processing_delay_ms=200,
        enable_websockets=True,
        cors_origins=["http://localhost:3000"]
    )
    
    print(f"📡 Configuring server on port {config.mock_api_port}")
    
    # Start server (in a real scenario, this would run in background)
    success = api_server.start_server(config)
    
    if success:
        print("✅ MockAPIServer started successfully!")
        
        # Get server info
        server_info = api_server.get_server_info()
        print(f"🌐 Server URL: {server_info.url}")
        print(f"📊 Server Status: {server_info.status}")
        
        print("\n📋 Available Endpoints:")
        endpoints = [
            "GET  /health - Health check",
            "POST /auth/login - User authentication",
            "POST /auth/register - User registration",
            "GET  /users/me - Current user profile",
            "POST /conversation/chat - Chat with AI",
            "GET  /conversations/{user_id}/history - Conversation history",
            "POST /emotion-analysis/analyze - Emotion analysis",
            "GET  /cultural-context/context - Cultural context analysis",
            "POST /cultural-context/analyze - Cultural deflection detection",
            "POST /speech/transcribe - Speech transcription",
            "POST /dissonance-detector/analyze - Voice-truth dissonance",
            "GET  /baseline-tracker/baseline/{user_id} - User baseline data",
            "POST /baseline-tracker/baseline/update - Update baseline",
            "POST /safety-moderation/validate - Content safety validation",
            "WS   /ws/{user_id} - WebSocket real-time communication"
        ]
        
        for endpoint in endpoints:
            print(f"  • {endpoint}")
        
        print(f"\n🔧 Configuration:")
        print(f"  • Processing Delay: {config.processing_delay_ms}ms")
        print(f"  • WebSocket Support: {'✅' if config.enable_websockets else '❌'}")
        print(f"  • CORS Origins: {', '.join(config.cors_origins)}")
        
        print(f"\n💡 To test the API:")
        print(f"  • Open your browser to {server_info.url}/health")
        print(f"  • Use curl: curl {server_info.url}/health")
        print(f"  • Connect frontend to: {server_info.url}")
        
        # Simulate running for a short time
        print(f"\n⏱️  Server running... (demo mode)")
        time.sleep(2)
        
        # Stop server
        api_server.stop_server()
        print("🛑 MockAPIServer stopped")
        
    else:
        print("❌ Failed to start MockAPIServer")


if __name__ == "__main__":
    asyncio.run(run_api_server_demo())