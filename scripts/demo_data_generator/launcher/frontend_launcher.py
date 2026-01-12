"""
Frontend Launcher Implementation

This module provides the FrontendLauncher class that manages the React frontend
application startup, configuration, and browser integration for the demo system.
"""

import os
import sys
import json
import time
import shutil
import subprocess
import webbrowser
import platform
import signal
import psutil
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime

from ..interfaces import FrontendLauncherInterface
from ..models import ServiceConfig, ProcessInfo


class FrontendLauncher(FrontendLauncherInterface):
    """
    Manages frontend application lifecycle including:
    - Package manager detection (npm/yarn)
    - Dependency installation
    - Environment configuration
    - Development server startup
    - Browser integration
    - Process monitoring and cleanup
    """
    
    def __init__(self, logger=None):
        """Initialize the frontend launcher"""
        self.logger = logger
        self.frontend_process: Optional[subprocess.Popen] = None
        self.frontend_path: Optional[str] = None
        self.package_manager: Optional[str] = None
        self.process_info: Optional[ProcessInfo] = None
        self.browser_process: Optional[subprocess.Popen] = None
        self.cleanup_handlers_registered = False
        
    def _log(self, level: str, message: str, **kwargs):
        """Internal logging helper"""
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
        else:
            print(f"[{level.upper()}] {message}")
    
    def _detect_package_manager(self, frontend_path: str) -> str:
        """
        Detect available package manager (npm or yarn)
        
        Args:
            frontend_path: Path to frontend directory
            
        Returns:
            Package manager command ('npm' or 'yarn')
            
        Raises:
            RuntimeError: If no package manager is available
        """
        self._log("debug", f"Detecting package manager in {frontend_path}")
        
        # Determine correct command names for platform
        yarn_cmd = "yarn.cmd" if platform.system() == "Windows" else "yarn"
        npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
        
        # Check for yarn.lock first (yarn preferred if available)
        yarn_lock = Path(frontend_path) / "yarn.lock"
        if yarn_lock.exists():
            if shutil.which(yarn_cmd):
                self._log("info", "Detected yarn as package manager")
                return "yarn"
            else:
                self._log("warning", "yarn.lock found but yarn not installed, falling back to npm")
        
        # Check for npm
        if shutil.which(npm_cmd):
            self._log("info", "Using npm as package manager")
            return "npm"
        
        # Check for package-lock.json
        package_lock = Path(frontend_path) / "package-lock.json"
        if package_lock.exists() and shutil.which(npm_cmd):
            self._log("info", "Detected npm from package-lock.json")
            return "npm"
        
        raise RuntimeError("No package manager (npm or yarn) found. Please install Node.js and npm.")
    
    def _check_node_version(self) -> Tuple[bool, str]:
        """
        Check if Node.js version is compatible
        
        Returns:
            Tuple of (is_compatible, version_string)
        """
        try:
            node_cmd = "node.exe" if platform.system() == "Windows" else "node"
            result = subprocess.run(
                [node_cmd, "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self._log("info", f"Node.js version: {version}")
                
                # Extract major version number
                major_version = int(version.lstrip('v').split('.')[0])
                is_compatible = major_version >= 14  # React requires Node 14+
                
                return is_compatible, version
            else:
                return False, "Not found"
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError) as e:
            self._log("error", f"Failed to check Node.js version: {e}")
            return False, "Error checking version"
    
    def _install_dependencies(self, frontend_path: str, package_manager: str) -> bool:
        """
        Install frontend dependencies
        
        Args:
            frontend_path: Path to frontend directory
            package_manager: Package manager to use ('npm' or 'yarn')
            
        Returns:
            True if installation successful, False otherwise
        """
        self._log("info", f"Installing dependencies using {package_manager}")
        
        try:
            # Check if node_modules exists and is recent
            node_modules = Path(frontend_path) / "node_modules"
            package_json = Path(frontend_path) / "package.json"
            
            if (node_modules.exists() and 
                package_json.exists() and 
                node_modules.stat().st_mtime > package_json.stat().st_mtime):
                self._log("info", "Dependencies appear to be up to date, skipping installation")
                return True
            
            # Install command based on package manager
            if package_manager == "yarn":
                yarn_cmd = "yarn.cmd" if platform.system() == "Windows" else "yarn"
                cmd = [yarn_cmd, "install", "--frozen-lockfile"]
            else:
                npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
                cmd = [npm_cmd, "ci" if Path(frontend_path, "package-lock.json").exists() else "install"]
            
            self._log("info", f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=frontend_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self._log("info", "Dependencies installed successfully")
                return True
            else:
                self._log("error", f"Dependency installation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self._log("error", "Dependency installation timed out")
            return False
        except Exception as e:
            self._log("error", f"Error installing dependencies: {e}")
            return False
    
    def _find_available_port(self, start_port: int, max_attempts: int = 10) -> int:
        """
        Find an available port starting from start_port
        
        Args:
            start_port: Port to start checking from
            max_attempts: Maximum number of ports to try
            
        Returns:
            Available port number
            
        Raises:
            RuntimeError: If no available port found
        """
        import socket
        
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.bind(('localhost', port))
                    self._log("debug", f"Port {port} is available")
                    return port
            except OSError:
                self._log("debug", f"Port {port} is in use")
                continue
        
        raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")
    
    def setup_environment(self, frontend_path: str) -> bool:
        """
        Setup frontend environment and dependencies
        
        Args:
            frontend_path: Path to frontend directory
            
        Returns:
            True if setup successful, False otherwise
        """
        self._log("info", f"Setting up frontend environment at {frontend_path}")
        
        try:
            # Validate frontend path
            frontend_dir = Path(frontend_path)
            if not frontend_dir.exists():
                self._log("error", f"Frontend directory does not exist: {frontend_path}")
                return False
            
            package_json = frontend_dir / "package.json"
            if not package_json.exists():
                self._log("error", f"package.json not found in {frontend_path}")
                return False
            
            # Check Node.js version
            node_compatible, node_version = self._check_node_version()
            if not node_compatible:
                self._log("error", f"Incompatible Node.js version: {node_version}. Requires Node.js 14+")
                return False
            
            # Detect and store package manager
            self.package_manager = self._detect_package_manager(frontend_path)
            self.frontend_path = frontend_path
            
            # Install dependencies
            if not self._install_dependencies(frontend_path, self.package_manager):
                return False
            
            self._log("info", "Frontend environment setup completed successfully")
            return True
            
        except Exception as e:
            self._log("error", f"Failed to setup frontend environment: {e}")
            return False
    
    def configure_api_endpoints(self, mock_api_url: str) -> bool:
        """
        Configure frontend to use mock API endpoints
        
        Args:
            mock_api_url: URL of the mock API server
            
        Returns:
            True if configuration successful, False otherwise
        """
        self._log("info", f"Configuring API endpoints to use {mock_api_url}")
        
        try:
            if not self.frontend_path:
                self._log("error", "Frontend path not set. Call setup_environment first.")
                return False
            
            # Create or update .env.local file for React
            env_file = Path(self.frontend_path) / ".env.local"
            
            env_content = f"""# Demo Data Generator Configuration
REACT_APP_API_BASE_URL={mock_api_url}
REACT_APP_WEBSOCKET_URL={mock_api_url.replace('http', 'ws')}
REACT_APP_DEMO_MODE=true
GENERATE_SOURCEMAP=false
"""
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            self._log("info", f"Created environment configuration at {env_file}")
            
            # Also check if there's a config file to update
            config_files = [
                Path(self.frontend_path) / "src" / "config" / "api.js",
                Path(self.frontend_path) / "src" / "config" / "api.ts",
                Path(self.frontend_path) / "src" / "services" / "api.js",
                Path(self.frontend_path) / "src" / "services" / "api.ts"
            ]
            
            for config_file in config_files:
                if config_file.exists():
                    self._log("info", f"Found API config file: {config_file}")
                    # Note: In a real implementation, we might want to modify these files
                    # For now, we rely on environment variables
            
            return True
            
        except Exception as e:
            self._log("error", f"Failed to configure API endpoints: {e}")
            return False
    
    def start_frontend(self, config: ServiceConfig) -> ProcessInfo:
        """
        Start frontend development server
        
        Args:
            config: Service configuration
            
        Returns:
            ProcessInfo with server details
            
        Raises:
            RuntimeError: If frontend fails to start
        """
        self._log("info", "Starting frontend development server")
        
        try:
            if not self.frontend_path or not self.package_manager:
                raise RuntimeError("Frontend environment not set up. Call setup_environment first.")
            
            # Register cleanup handlers
            self._register_cleanup_handlers()
            
            # Find available port
            try:
                port = self._find_available_port(config.frontend_port)
            except RuntimeError:
                # If preferred port range is full, try a wider range
                port = self._find_available_port(3000, 100)
            
            # Prepare environment variables
            env = os.environ.copy()
            env['PORT'] = str(port)
            env['BROWSER'] = 'none'  # Prevent automatic browser opening
            env['CI'] = 'true'  # Prevent interactive prompts
            
            # Start command based on package manager
            if self.package_manager == "yarn":
                yarn_cmd = "yarn.cmd" if platform.system() == "Windows" else "yarn"
                cmd = [yarn_cmd, "start"]
            else:
                npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
                cmd = [npm_cmd, "start"]
            
            self._log("info", f"Starting frontend with command: {' '.join(cmd)} on port {port}")
            
            # Start the process
            self.frontend_process = subprocess.Popen(
                cmd,
                cwd=self.frontend_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start (check for "compiled successfully" or similar)
            start_time = time.time()
            timeout = 60  # 60 second timeout
            server_ready = False
            
            while time.time() - start_time < timeout:
                if self.frontend_process.poll() is not None:
                    # Process has terminated
                    stdout, stderr = self.frontend_process.communicate()
                    raise RuntimeError(f"Frontend process terminated unexpectedly:\nSTDOUT: {stdout}\nSTDERR: {stderr}")
                
                # Check if server is responding
                try:
                    import urllib.request
                    urllib.request.urlopen(f"http://localhost:{port}", timeout=1)
                    server_ready = True
                    break
                except:
                    time.sleep(1)
            
            if not server_ready:
                self.stop_frontend()
                raise RuntimeError("Frontend server failed to start within timeout period")
            
            # Create process info
            self.process_info = ProcessInfo(
                process_id=self.frontend_process.pid,
                name="React Development Server",
                port=port,
                status="running",
                start_time=datetime.now(),
                url=f"http://localhost:{port}"
            )
            
            self._log("info", f"Frontend server started successfully on port {port}")
            return self.process_info
            
        except Exception as e:
            self._log("error", f"Failed to start frontend: {e}")
            raise RuntimeError(f"Failed to start frontend: {e}")
    
    def open_browser(self, url: str) -> bool:
        """
        Open browser to demo URL with cross-platform support
        
        Args:
            url: URL to open
            
        Returns:
            True if browser opened successfully, False otherwise
        """
        self._log("info", f"Opening browser to {url}")
        
        try:
            # Register browser controller for better control
            browser_opened = False
            
            # Try different browser opening strategies based on platform
            if platform.system() == "Windows":
                browser_opened = self._open_browser_windows(url)
            elif platform.system() == "Darwin":  # macOS
                browser_opened = self._open_browser_macos(url)
            else:  # Linux and others
                browser_opened = self._open_browser_linux(url)
            
            if browser_opened:
                self._log("info", "Browser opened successfully")
                return True
            else:
                # Fallback to webbrowser module
                success = webbrowser.open(url)
                if success:
                    self._log("info", "Browser opened using fallback method")
                    return True
                else:
                    self._log("warning", "Failed to open browser automatically")
                    self._log("info", f"Please manually open your browser to: {url}")
                    return False
                
        except Exception as e:
            self._log("error", f"Error opening browser: {e}")
            self._log("info", f"Please manually open your browser to: {url}")
            return False
    
    def _open_browser_windows(self, url: str) -> bool:
        """Open browser on Windows"""
        try:
            # Try to use the default browser
            subprocess.run(['start', url], shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            # Try alternative methods
            try:
                subprocess.run(['cmd', '/c', 'start', url], check=True)
                return True
            except subprocess.CalledProcessError:
                return False
    
    def _open_browser_macos(self, url: str) -> bool:
        """Open browser on macOS"""
        try:
            subprocess.run(['open', url], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _open_browser_linux(self, url: str) -> bool:
        """Open browser on Linux"""
        try:
            # Try xdg-open first (most common)
            subprocess.run(['xdg-open', url], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try other common browsers
            browsers = ['firefox', 'google-chrome', 'chromium-browser', 'chromium']
            for browser in browsers:
                try:
                    subprocess.run([browser, url], check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            return False
    
    def _register_cleanup_handlers(self):
        """Register cleanup handlers for graceful shutdown"""
        if self.cleanup_handlers_registered:
            return
        
        def cleanup_handler(signum, frame):
            self._log("info", "Received shutdown signal, cleaning up...")
            self.stop_frontend()
            sys.exit(0)
        
        # Register signal handlers for graceful shutdown
        if platform.system() != "Windows":
            signal.signal(signal.SIGTERM, cleanup_handler)
            signal.signal(signal.SIGINT, cleanup_handler)
        
        self.cleanup_handlers_registered = True
    
    def monitor_process_health(self) -> Dict[str, any]:
        """
        Monitor the health of the frontend process
        
        Returns:
            Dictionary with process health information
        """
        health_info = {
            "is_running": False,
            "cpu_percent": 0.0,
            "memory_mb": 0.0,
            "uptime_seconds": 0.0,
            "port_accessible": False,
            "error": None
        }
        
        try:
            if not self.frontend_process or not self.process_info:
                health_info["error"] = "No process to monitor"
                return health_info
            
            # Check if process is still running
            if self.frontend_process.poll() is not None:
                health_info["error"] = "Process has terminated"
                return health_info
            
            health_info["is_running"] = True
            
            # Get process information using psutil
            try:
                process = psutil.Process(self.frontend_process.pid)
                health_info["cpu_percent"] = process.cpu_percent()
                health_info["memory_mb"] = process.memory_info().rss / 1024 / 1024
                health_info["uptime_seconds"] = (datetime.now() - self.process_info.start_time).total_seconds()
            except psutil.NoSuchProcess:
                health_info["error"] = "Process not found in system"
                health_info["is_running"] = False
                return health_info
            
            # Check if port is accessible
            if self.process_info.port:
                health_info["port_accessible"] = self._check_port_accessible(self.process_info.port)
            
        except Exception as e:
            health_info["error"] = str(e)
        
        return health_info
    
    def _check_port_accessible(self, port: int) -> bool:
        """Check if a port is accessible"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except:
            return False
    
    def restart_frontend(self, config: ServiceConfig) -> ProcessInfo:
        """
        Restart the frontend server
        
        Args:
            config: Service configuration
            
        Returns:
            ProcessInfo with new server details
        """
        self._log("info", "Restarting frontend server")
        
        # Stop current instance
        self.stop_frontend()
        
        # Wait a moment for cleanup
        time.sleep(2)
        
        # Start new instance
        return self.start_frontend(config)
    
    def get_process_logs(self, lines: int = 50) -> Dict[str, List[str]]:
        """
        Get recent logs from the frontend process
        
        Args:
            lines: Number of recent lines to retrieve
            
        Returns:
            Dictionary with stdout and stderr logs
        """
        logs = {
            "stdout": [],
            "stderr": [],
            "error": None
        }
        
        try:
            if not self.frontend_process:
                logs["error"] = "No process to get logs from"
                return logs
            
            # Note: In a production implementation, we might want to
            # redirect process output to log files for better log management
            # For now, we'll return a placeholder
            logs["stdout"] = ["Frontend process is running"]
            logs["stderr"] = []
            
        except Exception as e:
            logs["error"] = str(e)
        
        return logs
    
    def kill_process_tree(self, pid: int):
        """
        Kill a process and all its children (cross-platform)
        
        Args:
            pid: Process ID to kill
        """
        try:
            if platform.system() == "Windows":
                # Use taskkill on Windows
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                             capture_output=True, check=False)
            else:
                # Use kill on Unix-like systems
                try:
                    parent = psutil.Process(pid)
                    children = parent.children(recursive=True)
                    
                    # Kill children first
                    for child in children:
                        try:
                            child.terminate()
                        except psutil.NoSuchProcess:
                            pass
                    
                    # Wait for children to terminate
                    gone, alive = psutil.wait_procs(children, timeout=3)
                    
                    # Force kill any remaining children
                    for child in alive:
                        try:
                            child.kill()
                        except psutil.NoSuchProcess:
                            pass
                    
                    # Finally kill the parent
                    parent.terminate()
                    parent.wait(timeout=3)
                    
                except psutil.TimeoutExpired:
                    parent.kill()
                except psutil.NoSuchProcess:
                    pass  # Process already gone
                    
        except Exception as e:
            self._log("warning", f"Error killing process tree: {e}")
    
    def cleanup_resources(self):
        """Clean up all resources and processes"""
        self._log("info", "Cleaning up frontend launcher resources")
        
        try:
            # Stop frontend process
            if self.frontend_process:
                self.kill_process_tree(self.frontend_process.pid)
                self.frontend_process = None
            
            # Close browser if we opened it
            if self.browser_process:
                try:
                    self.browser_process.terminate()
                    self.browser_process = None
                except:
                    pass
            
            # Clean up temporary files if any
            if self.frontend_path:
                env_file = Path(self.frontend_path) / ".env.local"
                if env_file.exists():
                    try:
                        # Only remove if it contains our demo configuration
                        with open(env_file, 'r') as f:
                            content = f.read()
                        if "Demo Data Generator Configuration" in content:
                            env_file.unlink()
                            self._log("info", "Cleaned up demo environment file")
                    except Exception as e:
                        self._log("warning", f"Could not clean up environment file: {e}")
            
            self.process_info = None
            self._log("info", "Resource cleanup completed")
            
        except Exception as e:
            self._log("error", f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup_resources()
        except:
            pass  # Ignore errors during destruction
    
    def stop_frontend(self) -> bool:
        """
        Stop frontend server with enhanced process management
        
        Returns:
            True if stopped successfully, False otherwise
        """
        self._log("info", "Stopping frontend server")
        
        try:
            if self.frontend_process is None:
                self._log("info", "No frontend process to stop")
                return True
            
            pid = self.frontend_process.pid
            
            # Try graceful shutdown first
            self.frontend_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.frontend_process.wait(timeout=10)
                self._log("info", "Frontend server stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't stop gracefully
                self._log("warning", "Frontend server didn't stop gracefully, forcing termination")
                self.kill_process_tree(pid)
            
            # Update process info
            if self.process_info:
                self.process_info.status = "stopped"
            
            self.frontend_process = None
            self._log("info", "Frontend server stopped successfully")
            return True
            
        except Exception as e:
            self._log("error", f"Error stopping frontend server: {e}")
            return False
    
    def get_process_info(self) -> Optional[ProcessInfo]:
        """
        Get current process information
        
        Returns:
            ProcessInfo if server is running, None otherwise
        """
        if self.process_info and self.frontend_process:
            # Update status based on process state
            if self.frontend_process.poll() is None:
                self.process_info.status = "running"
            else:
                self.process_info.status = "stopped"
        
        return self.process_info
    
    def is_running(self) -> bool:
        """
        Check if frontend server is currently running
        
        Returns:
            True if running, False otherwise
        """
        return (self.frontend_process is not None and 
                self.frontend_process.poll() is None)
    
    def get_server_url(self) -> Optional[str]:
        """
        Get the URL of the running frontend server
        
        Returns:
            Server URL if running, None otherwise
        """
        if self.process_info and self.is_running():
            return self.process_info.url
        return None