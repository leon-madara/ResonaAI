#!/usr/bin/env python3
"""
Demo Data Generator Entry Point

This script provides the main entry point for the ResonaAI Demo Data Generator.
It can be used to generate test data, launch the demo environment, and manage
the complete demonstration system.

Usage:
    python demo_data_generator.py generate --preset quick
    python demo_data_generator.py launch --auto-browser
    python demo_data_generator.py cleanup
"""

import argparse
import sys
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add the ResonaAI root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from demo_data_generator.config import (
    ConfigurationManager, 
    apply_preset,
    QUICK_DEMO_CONFIG,
    COMPREHENSIVE_DEMO_CONFIG,
    DEVELOPMENT_CONFIG
)
from demo_data_generator.models import DemoConfig, ServiceConfig, GenerationResult
from demo_data_generator.storage.local_storage import LocalStorageManager
from demo_data_generator.generators.user_generator import UserGenerator
from demo_data_generator.generators.conversation_simulator import ConversationSimulator
from demo_data_generator.generators.cultural_generator import CulturalGenerator
from demo_data_generator.generators.emotion_generator import EmotionGenerator
from demo_data_generator.generators.voice_simulator import VoiceSimulator
from demo_data_generator.api.mock_api_server import MockAPIServer
from demo_data_generator.launcher.frontend_launcher import FrontendLauncher


class DemoDataGenerator:
    """
    Main orchestrator for the Demo Data Generator system.
    
    Coordinates all data generation components, manages progress reporting,
    and handles configuration for demo parameters.
    """
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        """Initialize the demo data generator with configuration"""
        self.config_manager = config_manager or ConfigurationManager()
        self.logger = self._setup_logging()
        
        # Initialize storage manager
        demo_config = self.config_manager.get_demo_config()
        self.storage = LocalStorageManager(demo_config.output_directory)
        
        # Initialize generators
        self.user_generator = UserGenerator(demo_config)
        self.conversation_simulator = ConversationSimulator()
        self.cultural_generator = CulturalGenerator()
        self.emotion_generator = EmotionGenerator()
        self.voice_simulator = VoiceSimulator()
        
        # Initialize services
        self.mock_api_server = MockAPIServer(self.storage)
        self.frontend_launcher = FrontendLauncher(self.logger)
        
        # Track generation progress
        self.generation_progress = {
            "total_steps": 0,
            "completed_steps": 0,
            "current_step": "",
            "start_time": None,
            "errors": [],
            "warnings": []
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the demo data generator"""
        logger = logging.getLogger("demo_data_generator")
        logger.setLevel(logging.INFO)
        
        # Create console handler if not already exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def generate_all_data(self, config: Optional[DemoConfig] = None) -> GenerationResult:
        """
        Generate all demo data according to configuration.
        
        Args:
            config: Optional demo configuration, uses default if not provided
            
        Returns:
            GenerationResult with generation statistics and status
        """
        if config:
            self.config_manager.update_demo_config(config)
        
        demo_config = self.config_manager.get_demo_config()
        
        self.logger.info("🚀 Starting comprehensive demo data generation")
        self.logger.info(f"📊 Configuration: {demo_config.num_users} users, "
                        f"{demo_config.conversations_per_user} conversations each")
        
        # Initialize progress tracking
        self.generation_progress = {
            "total_steps": 6,  # User profiles, conversations, cultural data, emotions, voice data, storage
            "completed_steps": 0,
            "current_step": "Initializing",
            "start_time": datetime.now(),
            "errors": [],
            "warnings": []
        }
        
        try:
            # Step 1: Generate user profiles
            self._update_progress("Generating user profiles")
            user_result = self.user_generator.generate(demo_config)
            if not user_result.success:
                self.generation_progress["errors"].extend(user_result.errors)
                return self._create_failed_result("User generation failed", user_result.errors)
            
            # Save user data
            users_data = {"users": [profile.model_dump(mode='json') for profile in self.user_generator.generated_profiles]}
            if not self.storage.save_data("users", users_data):
                return self._create_failed_result("Failed to save user data")
            
            self._complete_step()
            
            # Step 2: Generate conversations for each user
            self._update_progress("Generating conversations")
            total_conversations = 0
            conversations_data = {"conversations": []}
            
            for i in range(demo_config.num_users):
                user_id = f"user_{i+1:03d}"
                for j in range(demo_config.conversations_per_user):
                    # Vary conversation scenarios
                    scenarios = list(self.conversation_simulator.conversation_templates.keys())
                    scenario = scenarios[j % len(scenarios)]
                    
                    conversation = self.conversation_simulator.generate_conversation_thread(scenario, user_id)
                    conversations_data["conversations"].append(conversation.model_dump(mode='json'))
                    total_conversations += 1
            
            if not self.storage.save_data("conversations", conversations_data):
                return self._create_failed_result("Failed to save conversation data")
            
            self._complete_step()
            
            # Step 3: Generate cultural scenarios and patterns
            self._update_progress("Generating cultural context data")
            cultural_result = self.cultural_generator.generate(demo_config)
            if not cultural_result.success:
                self.generation_progress["errors"].extend(cultural_result.errors)
                return self._create_failed_result("Cultural generation failed", cultural_result.errors)
            
            self._complete_step()
            
            # Step 4: Generate emotion analysis data
            self._update_progress("Generating emotion analysis data")
            emotion_result = self.emotion_generator.generate(demo_config)
            if not emotion_result.success:
                self.generation_progress["errors"].extend(emotion_result.errors)
                return self._create_failed_result("Emotion generation failed", emotion_result.errors)
            
            self._complete_step()
            
            # Step 5: Generate voice analysis data
            self._update_progress("Generating voice analysis data")
            voice_result = self.voice_simulator.generate(demo_config)
            if not voice_result.success:
                self.generation_progress["errors"].extend(voice_result.errors)
                return self._create_failed_result("Voice generation failed", voice_result.errors)
            
            self._complete_step()
            
            # Step 6: Validate and finalize
            self._update_progress("Validating generated data")
            validation_result = self.storage.validate_data_integrity()
            if not validation_result.valid:
                self.generation_progress["warnings"].extend(validation_result.validation_errors)
            
            self._complete_step()
            
            # Create final result
            generation_time = (datetime.now() - self.generation_progress["start_time"]).total_seconds()
            
            result = GenerationResult(
                success=True,
                users_generated=demo_config.num_users,
                conversations_generated=total_conversations,
                cultural_scenarios_generated=cultural_result.cultural_scenarios_generated,
                swahili_patterns_generated=cultural_result.swahili_patterns_generated,
                output_directory=demo_config.output_directory,
                generation_time_seconds=generation_time,
                warnings=self.generation_progress["warnings"]
            )
            
            self.logger.info(f"✅ Data generation completed successfully in {generation_time:.2f}s")
            self.logger.info(f"📈 Generated: {result.users_generated} users, "
                           f"{result.conversations_generated} conversations, "
                           f"{result.cultural_scenarios_generated} cultural scenarios")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Data generation failed: {e}")
            return self._create_failed_result(f"Unexpected error: {e}")
    
    def launch_complete_demo(self, auto_browser: bool = True, config: Optional[ServiceConfig] = None) -> Dict[str, Any]:
        """
        Launch the complete demo environment with mock API and frontend.
        
        Args:
            auto_browser: Whether to automatically open browser
            config: Optional service configuration
            
        Returns:
            Dictionary with launch status and service information
        """
        if config:
            self.config_manager.update_service_config(config)
        
        service_config = self.config_manager.get_service_config()
        
        self.logger.info("🚀 Launching complete demo environment")
        
        launch_result = {
            "success": False,
            "services": {},
            "urls": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Step 1: Start mock API server
            self.logger.info(f"🔧 Starting mock API server on port {service_config.mock_api_port}")
            if not self.mock_api_server.start_server(service_config):
                launch_result["errors"].append("Failed to start mock API server")
                return launch_result
            
            api_url = f"http://localhost:{service_config.mock_api_port}"
            launch_result["services"]["mock_api"] = {
                "status": "running",
                "url": api_url,
                "port": service_config.mock_api_port
            }
            launch_result["urls"]["api"] = api_url
            
            # Wait for API server to be ready
            time.sleep(2)
            
            # Step 2: Setup and start frontend
            frontend_path = self._find_frontend_path()
            if not frontend_path:
                launch_result["errors"].append("Frontend directory not found")
                return launch_result
            
            self.logger.info(f"🎨 Setting up frontend at {frontend_path}")
            if not self.frontend_launcher.setup_environment(frontend_path):
                launch_result["errors"].append("Failed to setup frontend environment")
                return launch_result
            
            # Configure frontend to use mock API
            if not self.frontend_launcher.configure_api_endpoints(api_url):
                launch_result["errors"].append("Failed to configure frontend API endpoints")
                return launch_result
            
            # Start frontend server
            self.logger.info(f"🎨 Starting frontend server")
            try:
                process_info = self.frontend_launcher.start_frontend(service_config)
                launch_result["services"]["frontend"] = {
                    "status": "running",
                    "url": process_info.url,
                    "port": process_info.port,
                    "process_id": process_info.process_id
                }
                launch_result["urls"]["frontend"] = process_info.url
                
            except RuntimeError as e:
                launch_result["errors"].append(f"Failed to start frontend: {e}")
                return launch_result
            
            # Step 3: Open browser if requested
            if auto_browser and service_config.auto_open_browser:
                self.logger.info("🌐 Opening browser")
                if not self.frontend_launcher.open_browser(process_info.url):
                    launch_result["warnings"].append("Failed to open browser automatically")
            
            launch_result["success"] = True
            
            self.logger.info("✅ Demo environment launched successfully!")
            self.logger.info(f"🌐 Frontend: {process_info.url}")
            self.logger.info(f"🔧 API: {api_url}")
            self.logger.info(f"📚 API Documentation: {api_url}/docs")
            
            return launch_result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to launch demo environment: {e}")
            launch_result["errors"].append(f"Unexpected error: {e}")
            return launch_result
    
    def cleanup_all_data(self) -> bool:
        """
        Clean up all demo data and stop running services.
        
        Returns:
            True if cleanup successful, False otherwise
        """
        self.logger.info("🧹 Starting comprehensive cleanup")
        
        cleanup_success = True
        
        try:
            # Stop services first
            self.logger.info("🛑 Stopping services")
            
            # Stop frontend
            if self.frontend_launcher.is_running():
                if not self.frontend_launcher.stop_frontend():
                    self.logger.warning("Failed to stop frontend server")
                    cleanup_success = False
            
            # Stop mock API server
            if not self.mock_api_server.stop_server():
                self.logger.warning("Failed to stop mock API server")
                cleanup_success = False
            
            # Clean up frontend resources
            self.frontend_launcher.cleanup_resources()
            
            # Clear all data files
            self.logger.info("🗑️ Clearing data files")
            if not self.storage.clear_all_data():
                self.logger.warning("Failed to clear all data files")
                cleanup_success = False
            
            # Validate clean state
            if not self.storage.validate_clean_state():
                self.logger.warning("Storage not in clean state after cleanup")
                cleanup_success = False
            
            if cleanup_success:
                self.logger.info("✅ Cleanup completed successfully")
            else:
                self.logger.warning("⚠️ Cleanup completed with some issues")
            
            return cleanup_success
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")
            return False
    
    def get_generation_progress(self) -> Dict[str, Any]:
        """
        Get current generation progress information.
        
        Returns:
            Dictionary with progress details
        """
        progress = self.generation_progress.copy()
        
        if progress["start_time"]:
            elapsed = (datetime.now() - progress["start_time"]).total_seconds()
            progress["elapsed_seconds"] = elapsed
            
            if progress["total_steps"] > 0:
                progress["progress_percentage"] = (progress["completed_steps"] / progress["total_steps"]) * 100
            else:
                progress["progress_percentage"] = 0
        
        return progress
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status including services and data.
        
        Returns:
            Dictionary with system status information
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "data": {},
            "configuration": {},
            "health": "unknown"
        }
        
        try:
            # Check service status
            status["services"]["mock_api"] = {
                "running": hasattr(self.mock_api_server, 'server') and self.mock_api_server.server is not None,
                "port": self.config_manager.get_service_config().mock_api_port
            }
            
            status["services"]["frontend"] = {
                "running": self.frontend_launcher.is_running(),
                "url": self.frontend_launcher.get_server_url()
            }
            
            # Check data status
            storage_summary = self.storage.get_storage_summary()
            status["data"] = {
                "total_files": storage_summary["total_files"],
                "total_size_bytes": storage_summary["total_size_bytes"],
                "last_modified": storage_summary["last_modified"].isoformat() if storage_summary["last_modified"] else None,
                "data_types": list(storage_summary["data_types"].keys())
            }
            
            # Configuration info
            demo_config = self.config_manager.get_demo_config()
            service_config = self.config_manager.get_service_config()
            
            status["configuration"] = {
                "demo": {
                    "users": demo_config.num_users,
                    "conversations_per_user": demo_config.conversations_per_user,
                    "output_directory": demo_config.output_directory
                },
                "services": {
                    "mock_api_port": service_config.mock_api_port,
                    "frontend_port": service_config.frontend_port,
                    "auto_open_browser": service_config.auto_open_browser
                }
            }
            
            # Determine overall health
            services_running = any(service["running"] for service in status["services"].values())
            has_data = status["data"]["total_files"] > 0
            
            if services_running and has_data:
                status["health"] = "healthy"
            elif services_running or has_data:
                status["health"] = "partial"
            else:
                status["health"] = "inactive"
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            status["health"] = "error"
            status["error"] = str(e)
        
        return status
    
    def _update_progress(self, step_name: str):
        """Update progress tracking"""
        self.generation_progress["current_step"] = step_name
        self.logger.info(f"📋 {step_name} ({self.generation_progress['completed_steps'] + 1}/{self.generation_progress['total_steps']})")
    
    def _complete_step(self):
        """Mark current step as completed"""
        self.generation_progress["completed_steps"] += 1
    
    def _create_failed_result(self, message: str, errors: Optional[list] = None) -> GenerationResult:
        """Create a failed generation result"""
        generation_time = 0
        if self.generation_progress["start_time"]:
            generation_time = (datetime.now() - self.generation_progress["start_time"]).total_seconds()
        
        return GenerationResult(
            success=False,
            users_generated=0,
            conversations_generated=0,
            cultural_scenarios_generated=0,
            swahili_patterns_generated=0,
            output_directory=self.config_manager.get_demo_config().output_directory,
            generation_time_seconds=generation_time,
            errors=[message] + (errors or [])
        )
    
    def _find_frontend_path(self) -> Optional[str]:
        """Find the frontend directory path"""
        # Look for frontend in common locations
        possible_paths = [
            Path(__file__).parent.parent / "apps" / "frontend",
            Path(__file__).parent.parent / "frontend",
            Path(__file__).parent.parent.parent / "apps" / "frontend",
            Path(__file__).parent.parent.parent / "frontend"
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "package.json").exists():
                return str(path)
        
        self.logger.warning("Frontend directory not found in expected locations")
        return None


class DemoDataGeneratorCLI:
    """Command-line interface for the Demo Data Generator"""
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.demo_generator = DemoDataGenerator(self.config_manager)
    
    def generate_data(self, preset: Optional[str] = None, config_file: Optional[str] = None) -> bool:
        """Generate demo data"""
        try:
            if config_file:
                self.config_manager = ConfigurationManager(config_file)
                self.demo_generator = DemoDataGenerator(self.config_manager)
            
            if preset:
                apply_preset(preset, self.config_manager)
            
            demo_config = self.config_manager.get_demo_config()
            
            print(f"🚀 Starting demo data generation...")
            print(f"📊 Configuration:")
            print(f"   - Users: {demo_config.num_users}")
            print(f"   - Conversations per user: {demo_config.conversations_per_user}")
            print(f"   - Cultural scenarios: {demo_config.cultural_scenarios}")
            print(f"   - Swahili patterns: {demo_config.swahili_patterns}")
            print(f"   - Output directory: {demo_config.output_directory}")
            print(f"   - Include crisis scenarios: {demo_config.include_crisis_scenarios}")
            
            # Generate all data using the orchestrator
            result = self.demo_generator.generate_all_data()
            
            if result.success:
                print(f"✅ Data generation completed successfully!")
                print(f"📈 Generated:")
                print(f"   - {result.users_generated} user profiles")
                print(f"   - {result.conversations_generated} conversations")
                print(f"   - {result.cultural_scenarios_generated} cultural scenarios")
                print(f"   - {result.swahili_patterns_generated} Swahili patterns")
                print(f"⏱️  Generation time: {result.generation_time_seconds:.2f} seconds")
                print(f"📁 Output directory: {result.output_directory}")
                
                if result.warnings:
                    print(f"⚠️  Warnings:")
                    for warning in result.warnings:
                        print(f"   - {warning}")
                
                return True
            else:
                print(f"❌ Data generation failed!")
                if result.errors:
                    print(f"Errors:")
                    for error in result.errors:
                        print(f"   - {error}")
                return False
            
        except Exception as e:
            print(f"❌ Error generating data: {e}")
            return False
    
    def launch_demo(self, auto_browser: bool = True, config_file: Optional[str] = None) -> bool:
        """Launch the complete demo environment"""
        try:
            if config_file:
                self.config_manager = ConfigurationManager(config_file)
                self.demo_generator = DemoDataGenerator(self.config_manager)
            
            service_config = self.config_manager.get_service_config()
            
            print(f"🚀 Starting demo environment...")
            print(f"🔧 Service configuration:")
            print(f"   - Mock API port: {service_config.mock_api_port}")
            print(f"   - Frontend port: {service_config.frontend_port}")
            print(f"   - Auto-open browser: {service_config.auto_open_browser and auto_browser}")
            print(f"   - Processing delay: {service_config.processing_delay_ms}ms")
            
            # Launch complete demo using the orchestrator
            result = self.demo_generator.launch_complete_demo(auto_browser)
            
            if result["success"]:
                print(f"✅ Demo environment launched successfully!")
                print(f"🌐 Frontend: {result['urls'].get('frontend', 'N/A')}")
                print(f"🔧 API Server: {result['urls'].get('api', 'N/A')}")
                print(f"📚 API Documentation: {result['urls'].get('api', 'N/A')}/docs")
                
                if result["warnings"]:
                    print(f"⚠️  Warnings:")
                    for warning in result["warnings"]:
                        print(f"   - {warning}")
                
                print(f"\n🎉 Demo is ready! Access the frontend at: {result['urls'].get('frontend', 'N/A')}")
                return True
            else:
                print(f"❌ Failed to launch demo environment!")
                if result["errors"]:
                    print(f"Errors:")
                    for error in result["errors"]:
                        print(f"   - {error}")
                return False
            
        except Exception as e:
            print(f"❌ Error launching demo: {e}")
            return False
    
    def cleanup_demo(self) -> bool:
        """Clean up demo data and stop services"""
        try:
            demo_config = self.config_manager.get_demo_config()
            
            print(f"🧹 Cleaning up demo data...")
            print(f"📁 Target directory: {demo_config.output_directory}")
            
            # Use orchestrator for cleanup
            success = self.demo_generator.cleanup_all_data()
            
            if success:
                print("✅ Cleanup completed successfully!")
            else:
                print("⚠️ Cleanup completed with some issues")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False
    
    def show_progress(self) -> bool:
        """Show current generation progress"""
        try:
            progress = self.demo_generator.get_generation_progress()
            
            print(f"📊 Generation Progress:")
            print(f"   - Current step: {progress['current_step']}")
            print(f"   - Completed: {progress['completed_steps']}/{progress['total_steps']}")
            
            if 'progress_percentage' in progress:
                print(f"   - Progress: {progress['progress_percentage']:.1f}%")
            
            if 'elapsed_seconds' in progress:
                print(f"   - Elapsed time: {progress['elapsed_seconds']:.1f}s")
            
            if progress['errors']:
                print(f"   - Errors: {len(progress['errors'])}")
                for error in progress['errors']:
                    print(f"     • {error}")
            
            if progress['warnings']:
                print(f"   - Warnings: {len(progress['warnings'])}")
                for warning in progress['warnings']:
                    print(f"     • {warning}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error getting progress: {e}")
            return False
    
    def show_status(self) -> bool:
        """Show comprehensive system status"""
        try:
            status = self.demo_generator.get_system_status()
            
            print(f"🔍 System Status ({status['timestamp']})")
            print(f"   - Overall health: {status['health'].upper()}")
            
            print(f"\n🔧 Services:")
            for service_name, service_info in status['services'].items():
                status_icon = "🟢" if service_info['running'] else "🔴"
                print(f"   {status_icon} {service_name}: {'Running' if service_info['running'] else 'Stopped'}")
                if 'url' in service_info and service_info['url']:
                    print(f"      URL: {service_info['url']}")
                if 'port' in service_info:
                    print(f"      Port: {service_info['port']}")
            
            print(f"\n📊 Data:")
            data_info = status['data']
            print(f"   - Files: {data_info['total_files']}")
            print(f"   - Size: {data_info['total_size_bytes']} bytes")
            print(f"   - Last modified: {data_info['last_modified'] or 'Never'}")
            print(f"   - Data types: {', '.join(data_info['data_types']) if data_info['data_types'] else 'None'}")
            
            print(f"\n⚙️ Configuration:")
            config_info = status['configuration']
            demo_config = config_info['demo']
            service_config = config_info['services']
            
            print(f"   Demo: {demo_config['users']} users, {demo_config['conversations_per_user']} conversations each")
            print(f"   Output: {demo_config['output_directory']}")
            print(f"   Ports: API={service_config['mock_api_port']}, Frontend={service_config['frontend_port']}")
            print(f"   Auto-browser: {service_config['auto_open_browser']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return False
    
    def validate_config(self, config_file: Optional[str] = None) -> bool:
        """Validate configuration"""
        try:
            if config_file:
                self.config_manager = ConfigurationManager(config_file)
            
            validation_results = self.config_manager.validate_configuration()
            
            print(f"🔍 Configuration Validation Results:")
            print(f"   - Valid: {'✅' if validation_results['valid'] else '❌'}")
            
            if validation_results['errors']:
                print(f"   - Errors:")
                for error in validation_results['errors']:
                    print(f"     • {error}")
            
            if validation_results['warnings']:
                print(f"   - Warnings:")
                for warning in validation_results['warnings']:
                    print(f"     • {warning}")
            
            return validation_results['valid']
            
        except Exception as e:
            print(f"❌ Error validating configuration: {e}")
            return False
    
    def show_config(self, config_file: Optional[str] = None) -> bool:
        """Show current configuration"""
        try:
            if config_file:
                self.config_manager = ConfigurationManager(config_file)
            
            demo_config = self.config_manager.get_demo_config()
            service_config = self.config_manager.get_service_config()
            env_info = self.config_manager.get_environment_info()
            
            print(f"📋 Current Configuration:")
            print(f"\n🎯 Demo Settings:")
            print(f"   - Users: {demo_config.num_users}")
            print(f"   - Conversations per user: {demo_config.conversations_per_user}")
            print(f"   - Cultural scenarios: {demo_config.cultural_scenarios}")
            print(f"   - Swahili patterns: {demo_config.swahili_patterns}")
            print(f"   - Output directory: {demo_config.output_directory}")
            print(f"   - Crisis scenarios: {demo_config.include_crisis_scenarios}")
            print(f"   - Crisis percentage: {demo_config.crisis_scenario_percentage}")
            
            print(f"\n🔧 Service Settings:")
            print(f"   - Mock API port: {service_config.mock_api_port}")
            print(f"   - Frontend port: {service_config.frontend_port}")
            print(f"   - Auto-open browser: {service_config.auto_open_browser}")
            print(f"   - Processing delay: {service_config.processing_delay_ms}ms")
            print(f"   - WebSockets enabled: {service_config.enable_websockets}")
            
            print(f"\n🌍 Environment:")
            print(f"   - Python: {env_info['python_version'].split()[0]}")
            print(f"   - Platform: {env_info['platform']}")
            print(f"   - Working directory: {env_info['working_directory']}")
            print(f"   - Config file: {env_info['config_file'] or 'None'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error showing configuration: {e}")
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ResonaAI Demo Data Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate --preset quick
  %(prog)s generate --config demo_config.json
  %(prog)s launch --auto-browser
  %(prog)s validate --config demo_config.json
  %(prog)s show-config
  %(prog)s status
  %(prog)s progress
  %(prog)s cleanup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate demo data')
    generate_parser.add_argument('--preset', choices=['quick', 'comprehensive', 'development'],
                                help='Use a configuration preset')
    generate_parser.add_argument('--config', help='Configuration file path')
    
    # Launch command
    launch_parser = subparsers.add_parser('launch', help='Launch demo environment')
    launch_parser.add_argument('--no-browser', action='store_true',
                              help='Do not auto-open browser')
    launch_parser.add_argument('--config', help='Configuration file path')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up demo data and stop services')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    validate_parser.add_argument('--config', help='Configuration file path')
    
    # Show config command
    show_parser = subparsers.add_parser('show-config', help='Show current configuration')
    show_parser.add_argument('--config', help='Configuration file path')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Progress command
    progress_parser = subparsers.add_parser('progress', help='Show generation progress')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = DemoDataGeneratorCLI()
    
    try:
        if args.command == 'generate':
            success = cli.generate_data(args.preset, getattr(args, 'config', None))
        elif args.command == 'launch':
            success = cli.launch_demo(not args.no_browser, getattr(args, 'config', None))
        elif args.command == 'cleanup':
            success = cli.cleanup_demo()
        elif args.command == 'validate':
            success = cli.validate_config(getattr(args, 'config', None))
        elif args.command == 'show-config':
            success = cli.show_config(getattr(args, 'config', None))
        elif args.command == 'status':
            success = cli.show_status()
        elif args.command == 'progress':
            success = cli.show_progress()
        else:
            parser.print_help()
            return 1
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())