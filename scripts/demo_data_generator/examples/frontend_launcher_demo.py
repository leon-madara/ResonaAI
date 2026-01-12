#!/usr/bin/env python3
"""
Frontend Launcher Demo

This script demonstrates how to use the FrontendLauncher to set up and start
the React frontend application for the demo system.
"""

import sys
import time
from pathlib import Path

# Add the demo_data_generator to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from demo_data_generator.launcher.frontend_launcher import FrontendLauncher
from demo_data_generator.models import ServiceConfig


def main():
    """Main demo function"""
    print("Frontend Launcher Demo")
    print("=" * 50)
    
    # Initialize the launcher
    launcher = FrontendLauncher()
    
    # Configure paths
    frontend_path = Path(__file__).parent.parent.parent.parent / "apps" / "frontend"
    
    print(f"Frontend path: {frontend_path}")
    
    if not frontend_path.exists():
        print("❌ Frontend directory not found!")
        print("Make sure you're running this from the correct location.")
        return 1
    
    try:
        # Step 1: Setup environment
        print("\n📦 Setting up frontend environment...")
        if not launcher.setup_environment(str(frontend_path)):
            print("❌ Failed to setup frontend environment")
            return 1
        print("✅ Frontend environment setup completed")
        
        # Step 2: Configure API endpoints
        print("\n🔧 Configuring API endpoints...")
        mock_api_url = "http://localhost:8001"
        if not launcher.configure_api_endpoints(mock_api_url):
            print("❌ Failed to configure API endpoints")
            return 1
        print(f"✅ API endpoints configured to use {mock_api_url}")
        
        # Step 3: Start frontend (this would normally start the server)
        print("\n🚀 Frontend launcher is ready!")
        print("In a real demo, this would:")
        print("  - Start the React development server")
        print("  - Open the browser automatically")
        print("  - Monitor the process health")
        
        # Create service config
        config = ServiceConfig(
            frontend_port=3000,
            auto_open_browser=True
        )
        
        print(f"\nConfiguration:")
        print(f"  - Frontend port: {config.frontend_port}")
        print(f"  - Auto open browser: {config.auto_open_browser}")
        print(f"  - Package manager: {launcher.package_manager}")
        
        # Demonstrate browser opening (without actually starting server)
        print("\n🌐 Testing browser integration...")
        test_url = "http://localhost:3000"
        if launcher.open_browser(test_url):
            print(f"✅ Browser integration working (opened {test_url})")
        else:
            print("⚠️  Browser integration had issues (this is normal in some environments)")
        
        print("\n✅ Frontend launcher demo completed successfully!")
        print("\nTo actually start the frontend server, you would call:")
        print("  process_info = launcher.start_frontend(config)")
        print("  # ... do demo work ...")
        print("  launcher.stop_frontend()")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return 1
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        launcher.cleanup_resources()
        print("✅ Cleanup completed")


if __name__ == "__main__":
    sys.exit(main())