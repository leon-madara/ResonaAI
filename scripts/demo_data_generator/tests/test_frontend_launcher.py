"""
Tests for Frontend Launcher

This module contains tests for the FrontendLauncher class functionality.
"""

import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from ..launcher.frontend_launcher import FrontendLauncher
from ..models import ServiceConfig, ProcessInfo


class TestFrontendLauncher:
    """Test cases for FrontendLauncher"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.launcher = FrontendLauncher()
        self.temp_dir = tempfile.mkdtemp()
        self.frontend_path = Path(self.temp_dir) / "frontend"
        self.frontend_path.mkdir()
        
        # Create a mock package.json
        package_json = {
            "name": "test-frontend",
            "version": "1.0.0",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            },
            "dependencies": {
                "react": "^18.0.0"
            }
        }
        
        with open(self.frontend_path / "package.json", 'w') as f:
            json.dump(package_json, f)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_package_manager_npm(self):
        """Test npm detection"""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = "/usr/bin/npm"
            
            package_manager = self.launcher._detect_package_manager(str(self.frontend_path))
            assert package_manager == "npm"
    
    def test_detect_package_manager_yarn(self):
        """Test yarn detection with yarn.lock"""
        # Create yarn.lock
        (self.frontend_path / "yarn.lock").touch()
        
        with patch('shutil.which') as mock_which:
            def which_side_effect(cmd):
                return "/usr/bin/yarn" if cmd == "yarn" else "/usr/bin/npm"
            mock_which.side_effect = which_side_effect
            
            package_manager = self.launcher._detect_package_manager(str(self.frontend_path))
            assert package_manager == "yarn"
    
    def test_detect_package_manager_no_manager(self):
        """Test error when no package manager available"""
        with patch('shutil.which', return_value=None):
            with pytest.raises(RuntimeError, match="No package manager"):
                self.launcher._detect_package_manager(str(self.frontend_path))
    
    @patch('subprocess.run')
    def test_check_node_version_compatible(self, mock_run):
        """Test compatible Node.js version check"""
        mock_run.return_value = Mock(returncode=0, stdout="v18.17.0\n")
        
        is_compatible, version = self.launcher._check_node_version()
        assert is_compatible is True
        assert version == "v18.17.0"
    
    @patch('subprocess.run')
    def test_check_node_version_incompatible(self, mock_run):
        """Test incompatible Node.js version check"""
        mock_run.return_value = Mock(returncode=0, stdout="v12.22.0\n")
        
        is_compatible, version = self.launcher._check_node_version()
        assert is_compatible is False
        assert version == "v12.22.0"
    
    def test_find_available_port(self):
        """Test finding available port"""
        port = self.launcher._find_available_port(3000)
        assert isinstance(port, int)
        assert port >= 3000
    
    def test_configure_api_endpoints(self):
        """Test API endpoint configuration"""
        self.launcher.frontend_path = str(self.frontend_path)
        
        success = self.launcher.configure_api_endpoints("http://localhost:8001")
        assert success is True
        
        # Check if .env.local was created
        env_file = self.frontend_path / ".env.local"
        assert env_file.exists()
        
        content = env_file.read_text()
        assert "REACT_APP_API_BASE_URL=http://localhost:8001" in content
        assert "REACT_APP_DEMO_MODE=true" in content
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_setup_environment_success(self, mock_which, mock_run):
        """Test successful environment setup"""
        mock_which.return_value = "/usr/bin/npm"
        mock_run.side_effect = [
            Mock(returncode=0, stdout="v18.17.0\n"),  # Node version check
            Mock(returncode=0)  # npm install
        ]
        
        # Mock node_modules to appear up to date
        node_modules = self.frontend_path / "node_modules"
        node_modules.mkdir()
        
        success = self.launcher.setup_environment(str(self.frontend_path))
        assert success is True
        assert self.launcher.package_manager == "npm"
        assert self.launcher.frontend_path == str(self.frontend_path)
    
    def test_setup_environment_no_package_json(self):
        """Test setup failure when package.json missing"""
        # Remove package.json
        (self.frontend_path / "package.json").unlink()
        
        success = self.launcher.setup_environment(str(self.frontend_path))
        assert success is False
    
    def test_monitor_process_health_no_process(self):
        """Test process health monitoring with no process"""
        health = self.launcher.monitor_process_health()
        assert health["is_running"] is False
        assert health["error"] == "No process to monitor"
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_open_browser_windows(self, mock_run, mock_system):
        """Test browser opening on Windows"""
        mock_system.return_value = "Windows"
        mock_run.return_value = Mock(returncode=0)
        
        success = self.launcher.open_browser("http://localhost:3000")
        assert success is True
        mock_run.assert_called_with(['start', 'http://localhost:3000'], shell=True, check=True)
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_open_browser_macos(self, mock_run, mock_system):
        """Test browser opening on macOS"""
        mock_system.return_value = "Darwin"
        mock_run.return_value = Mock(returncode=0)
        
        success = self.launcher.open_browser("http://localhost:3000")
        assert success is True
        mock_run.assert_called_with(['open', 'http://localhost:3000'], check=True)
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_open_browser_linux(self, mock_run, mock_system):
        """Test browser opening on Linux"""
        mock_system.return_value = "Linux"
        mock_run.return_value = Mock(returncode=0)
        
        success = self.launcher.open_browser("http://localhost:3000")
        assert success is True
        mock_run.assert_called_with(['xdg-open', 'http://localhost:3000'], check=True)
    
    def test_cleanup_resources(self):
        """Test resource cleanup"""
        # Set up some mock resources
        self.launcher.frontend_path = str(self.frontend_path)
        self.launcher.frontend_process = Mock()
        self.launcher.frontend_process.pid = 12345
        
        # Create demo env file
        env_file = self.frontend_path / ".env.local"
        env_file.write_text("# Demo Data Generator Configuration\nREACT_APP_API_BASE_URL=http://localhost:8001")
        
        with patch.object(self.launcher, 'kill_process_tree') as mock_kill:
            self.launcher.cleanup_resources()
            
            mock_kill.assert_called_once_with(12345)
            assert self.launcher.frontend_process is None
            assert not env_file.exists()  # Should be cleaned up
    
    def test_get_process_info_no_process(self):
        """Test getting process info when no process exists"""
        info = self.launcher.get_process_info()
        assert info is None
    
    def test_is_running_no_process(self):
        """Test is_running when no process exists"""
        assert self.launcher.is_running() is False
    
    def test_get_server_url_no_process(self):
        """Test getting server URL when no process exists"""
        url = self.launcher.get_server_url()
        assert url is None


if __name__ == "__main__":
    pytest.main([__file__])