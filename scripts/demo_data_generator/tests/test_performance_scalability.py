#!/usr/bin/env python3
"""
Performance and Scalability Testing

This module provides comprehensive performance and scalability tests for the
Demo Data Generator system, including benchmarking data generation times,
service startup performance, and frontend responsiveness validation.

Requirements tested: 6.1, 6.2
"""

import pytest
import time
import tempfile
import shutil
import psutil
import threading
import requests
import statistics
from pathlib import Path
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os

import sys
from pathlib import Path
import importlib.util

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from demo_data_generator.config import ConfigurationManager
from demo_data_generator.models import DemoConfig, ServiceConfig
from demo_data_generator.storage.local_storage import LocalStorageManager

# Import the main class from the script file directly
spec = importlib.util.spec_from_file_location("demo_data_generator_main", 
                                               Path(__file__).parent.parent.parent / "demo_data_generator.py")
demo_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo_module)

DemoDataGenerator = demo_module.DemoDataGenerator


class PerformanceMetrics:
    """Helper class to collect and analyze performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration"""
        if operation not in self.start_times:
            raise ValueError(f"Timer for {operation} was not started")
        
        duration = time.time() - self.start_times[operation]
        
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)
        
        return duration
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistical summary for an operation"""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}
        
        times = self.metrics[operation]
        return {
            "count": len(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get stats for all operations"""
        return {op: self.get_stats(op) for op in self.metrics.keys()}


class ResourceMonitor:
    """Monitor system resource usage during operations"""
    
    def __init__(self):
        self.monitoring = False
        self.samples = []
        self.monitor_thread = None
    
    def start_monitoring(self, interval: float = 0.5):
        """Start monitoring system resources"""
        self.monitoring = True
        self.samples = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return resource usage summary"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        if not self.samples:
            return {}
        
        # Calculate statistics
        cpu_values = [sample["cpu_percent"] for sample in self.samples]
        memory_values = [sample["memory_mb"] for sample in self.samples]
        
        return {
            "duration_seconds": len(self.samples) * 0.5,  # Approximate
            "cpu_percent": {
                "mean": statistics.mean(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory_mb": {
                "mean": statistics.mean(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "sample_count": len(self.samples)
        }
    
    def _monitor_loop(self, interval: float):
        """Internal monitoring loop"""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                sample = {
                    "timestamp": time.time(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_mb": process.memory_info().rss / 1024 / 1024
                }
                self.samples.append(sample)
                time.sleep(interval)
            except Exception:
                break  # Process might have ended


class TestDataGenerationPerformance:
    """Test data generation performance across different scales"""
    
    @pytest.fixture
    def temp_demo_dir(self):
        """Create temporary directory for performance tests"""
        temp_dir = tempfile.mkdtemp(prefix="perf_test_")
        yield temp_dir
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def performance_metrics(self):
        """Provide performance metrics collector"""
        return PerformanceMetrics()
    
    @pytest.fixture
    def resource_monitor(self):
        """Provide resource monitor"""
        return ResourceMonitor()
    
    def test_small_dataset_generation_benchmark(self, temp_demo_dir, performance_metrics, resource_monitor):
        """
        Benchmark data generation for small datasets
        Requirements: 6.1, 6.2
        """
        config = DemoConfig(
            num_users=5,
            conversations_per_user=3,
            cultural_scenarios=10,
            swahili_patterns=20,
            output_directory=temp_demo_dir,
            include_crisis_scenarios=True
        )
        
        config_manager = ConfigurationManager()
        config_manager.update_demo_config(config)
        generator = DemoDataGenerator(config_manager)
        
        print("🧪 Benchmarking small dataset generation...")
        
        # Run multiple iterations for statistical significance
        iterations = 3
        for i in range(iterations):
            # Clean directory for each iteration
            if Path(temp_demo_dir).exists():
                shutil.rmtree(temp_demo_dir)
            Path(temp_demo_dir).mkdir(parents=True, exist_ok=True)
            
            # Monitor resources
            resource_monitor.start_monitoring()
            performance_metrics.start_timer(f"small_dataset_iteration_{i}")
            
            result = generator.generate_all_data(config)
            
            duration = performance_metrics.end_timer(f"small_dataset_iteration_{i}")
            resource_usage = resource_monitor.stop_monitoring()
            
            assert result.success, f"Generation failed on iteration {i}: {result.errors}"
            
            print(f"   Iteration {i+1}: {duration:.2f}s, "
                  f"CPU: {resource_usage.get('cpu_percent', {}).get('mean', 0):.1f}%, "
                  f"Memory: {resource_usage.get('memory_mb', {}).get('max', 0):.1f}MB")
        
        # Analyze performance
        small_stats = performance_metrics.get_stats("small_dataset_iteration_0")
        all_times = []
        for i in range(iterations):
            stats = performance_metrics.get_stats(f"small_dataset_iteration_{i}")
            all_times.extend(performance_metrics.metrics[f"small_dataset_iteration_{i}"])
        
        mean_time = statistics.mean(all_times)
        max_time = max(all_times)
        
        # Performance assertions
        assert mean_time < 15, f"Small dataset generation too slow: {mean_time:.2f}s average"
        assert max_time < 25, f"Small dataset generation max time too slow: {max_time:.2f}s"
        
        print(f"✅ Small dataset benchmark: {mean_time:.2f}s average, {max_time:.2f}s max")
    
    def test_medium_dataset_generation_benchmark(self, temp_demo_dir, performance_metrics, resource_monitor):
        """
        Benchmark data generation for medium datasets
        Requirements: 6.1, 6.2
        """
        config = DemoConfig(
            num_users=15,
            conversations_per_user=5,
            cultural_scenarios=25,
            swahili_patterns=50,
            output_directory=temp_demo_dir,
            include_crisis_scenarios=True
        )
        
        config_manager = ConfigurationManager()
        config_manager.update_demo_config(config)
        generator = DemoDataGenerator(config_manager)
        
        print("🧪 Benchmarking medium dataset generation...")
        
        resource_monitor.start_monitoring()
        performance_metrics.start_timer("medium_dataset")
        
        result = generator.generate_all_data(config)
        
        duration = performance_metrics.end_timer("medium_dataset")
        resource_usage = resource_monitor.stop_monitoring()
        
        assert result.success, f"Medium dataset generation failed: {result.errors}"
        
        # Verify data completeness
        assert result.users_generated == config.num_users
        assert result.conversations_generated == config.num_users * config.conversations_per_user
        
        # Performance assertions
        assert duration < 45, f"Medium dataset generation too slow: {duration:.2f}s"
        
        # Resource usage assertions
        max_memory = resource_usage.get('memory_mb', {}).get('max', 0)
        assert max_memory < 500, f"Memory usage too high: {max_memory:.1f}MB"
        
        print(f"✅ Medium dataset benchmark: {duration:.2f}s, "
              f"Memory: {max_memory:.1f}MB, "
              f"CPU: {resource_usage.get('cpu_percent', {}).get('mean', 0):.1f}%")
    
    def test_large_dataset_generation_benchmark(self, temp_demo_dir, performance_metrics, resource_monitor):
        """
        Benchmark data generation for large datasets
        Requirements: 6.1, 6.2
        """
        config = DemoConfig(
            num_users=30,
            conversations_per_user=8,
            cultural_scenarios=50,
            swahili_patterns=100,
            output_directory=temp_demo_dir,
            include_crisis_scenarios=True
        )
        
        config_manager = ConfigurationManager()
        config_manager.update_demo_config(config)
        generator = DemoDataGenerator(config_manager)
        
        print("🧪 Benchmarking large dataset generation...")
        
        resource_monitor.start_monitoring()
        performance_metrics.start_timer("large_dataset")
        
        result = generator.generate_all_data(config)
        
        duration = performance_metrics.end_timer("large_dataset")
        resource_usage = resource_monitor.stop_monitoring()
        
        assert result.success, f"Large dataset generation failed: {result.errors}"
        
        # Verify data completeness
        assert result.users_generated == config.num_users
        assert result.conversations_generated == config.num_users * config.conversations_per_user
        
        # Performance assertions (more lenient for large datasets)
        assert duration < 120, f"Large dataset generation too slow: {duration:.2f}s"
        
        # Resource usage assertions
        max_memory = resource_usage.get('memory_mb', {}).get('max', 0)
        assert max_memory < 1000, f"Memory usage too high: {max_memory:.1f}MB"
        
        print(f"✅ Large dataset benchmark: {duration:.2f}s, "
              f"Memory: {max_memory:.1f}MB, "
              f"CPU: {resource_usage.get('cpu_percent', {}).get('mean', 0):.1f}%")
    
    def test_data_generation_scaling_analysis(self, temp_demo_dir, performance_metrics):
        """
        Analyze how data generation performance scales with dataset size
        Requirements: 6.1, 6.2
        """
        print("🧪 Analyzing data generation scaling...")
        
        # Test different scales
        test_configs = [
            {"users": 2, "conversations": 2, "name": "tiny"},
            {"users": 5, "conversations": 3, "name": "small"},
            {"users": 10, "conversations": 4, "name": "medium"},
            {"users": 20, "conversations": 5, "name": "large"}
        ]
        
        scaling_results = []
        
        for test_config in test_configs:
            # Clean directory
            if Path(temp_demo_dir).exists():
                shutil.rmtree(temp_demo_dir)
            Path(temp_demo_dir).mkdir(parents=True, exist_ok=True)
            
            config = DemoConfig(
                num_users=test_config["users"],
                conversations_per_user=test_config["conversations"],
                cultural_scenarios=10,
                swahili_patterns=20,
                output_directory=temp_demo_dir
            )
            
            config_manager = ConfigurationManager()
            config_manager.update_demo_config(config)
            generator = DemoDataGenerator(config_manager)
            
            performance_metrics.start_timer(f"scaling_{test_config['name']}")
            result = generator.generate_all_data(config)
            duration = performance_metrics.end_timer(f"scaling_{test_config['name']}")
            
            assert result.success, f"Generation failed for {test_config['name']}"
            
            total_items = result.users_generated + result.conversations_generated
            items_per_second = total_items / duration if duration > 0 else 0
            
            scaling_results.append({
                "name": test_config["name"],
                "users": test_config["users"],
                "conversations": test_config["conversations"],
                "total_items": total_items,
                "duration": duration,
                "items_per_second": items_per_second
            })
            
            print(f"   {test_config['name']}: {duration:.2f}s for {total_items} items "
                  f"({items_per_second:.1f} items/sec)")
        
        # Analyze scaling efficiency
        # Performance should not degrade dramatically with size
        tiny_rate = scaling_results[0]["items_per_second"]
        large_rate = scaling_results[-1]["items_per_second"]
        
        # Allow some degradation but not more than 50%
        efficiency_ratio = large_rate / tiny_rate if tiny_rate > 0 else 0
        assert efficiency_ratio > 0.5, f"Performance degradation too severe: {efficiency_ratio:.2f}"
        
        print(f"✅ Scaling analysis complete. Efficiency ratio: {efficiency_ratio:.2f}")


class TestServicePerformance:
    """Test service startup and runtime performance"""
    
    @pytest.fixture
    def temp_demo_dir(self):
        """Create temporary directory for service tests"""
        temp_dir = tempfile.mkdtemp(prefix="service_perf_")
        yield temp_dir
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_service_startup_performance_benchmark(self, temp_demo_dir):
        """
        Benchmark service startup times
        Requirements: 6.1, 6.2
        """
        config = DemoConfig(
            num_users=5,
            conversations_per_user=3,
            output_directory=temp_demo_dir
        )
        
        service_config = ServiceConfig(
            mock_api_port=8903,
            frontend_port=3903,
            auto_open_browser=False
        )
        
        config_manager = ConfigurationManager()
        config_manager.update_demo_config(config)
        config_manager.update_service_config(service_config)
        generator = DemoDataGenerator(config_manager)
        
        # Generate data first
        result = generator.generate_all_data(config)
        assert result.success, "Data generation failed"
        
        print("🧪 Benchmarking service startup performance...")
        
        startup_times = []
        iterations = 3
        
        for i in range(iterations):
            try:
                start_time = time.time()
                launch_result = generator.launch_complete_demo(auto_browser=False, config=service_config)
                startup_time = time.time() - start_time
                
                assert launch_result["success"], f"Service launch failed: {launch_result['errors']}"
                startup_times.append(startup_time)
                
                # Verify services are responsive
                api_url = launch_result["urls"]["api"]
                response = requests.get(f"{api_url}/health", timeout=10)
                assert response.status_code == 200, "API not responsive"
                
                print(f"   Iteration {i+1}: {startup_time:.2f}s")
                
            finally:
                # Cleanup for next iteration
                generator.cleanup_all_data()
                time.sleep(1)  # Brief pause between iterations
        
        # Analyze startup performance
        mean_startup = statistics.mean(startup_times)
        max_startup = max(startup_times)
        
        # Performance assertions
        assert mean_startup < 20, f"Service startup too slow: {mean_startup:.2f}s average"
        assert max_startup < 30, f"Service startup max time too slow: {max_startup:.2f}s"
        
        print(f"✅ Service startup benchmark: {mean_startup:.2f}s average, {max_startup:.2f}s max")
    
    def test_api_response_time_benchmark(self, temp_demo_dir):
        """
        Benchmark API response times under load
        Requirements: 6.2
        """
        config = DemoConfig(
            num_users=10,
            conversations_per_user=5,
            output_directory=temp_demo_dir
        )
        
        service_config = ServiceConfig(
            mock_api_port=8904,
            auto_open_browser=False,
            processing_delay_ms=5  # Minimal delay for performance testing
        )
        
        config_manager = ConfigurationManager()
        config_manager.update_demo_config(config)
        config_manager.update_service_config(service_config)
        generator = DemoDataGenerator(config_manager)
        
        # Setup
        result = generator.generate_all_data(config)
        assert result.success, "Data generation failed"
        
        launch_result = generator.launch_complete_demo(auto_browser=False, config=service_config)
        assert launch_result["success"], "Service launch failed"
        
        try:
            api_url = launch_result["urls"]["api"]
            time.sleep(2)  # Wait for services to be ready
            
            print("🧪 Benchmarking API response times...")
            
            # Test different endpoints
            endpoints_to_test = [
                {"path": "/health", "method": "GET"},
                {"path": "/api/users", "method": "GET"},
                {"path": "/api/cultural/patterns", "method": "GET"}
            ]
            
            response_times = {}
            
            for endpoint in endpoints_to_test:
                path = endpoint["path"]
                method = endpoint["method"]
                
                times = []
                iterations = 10
                
                for i in range(iterations):
                    start_time = time.time()
                    
                    if method == "GET":
                        response = requests.get(f"{api_url}{path}", timeout=10)
                    else:
                        continue  # Skip non-GET for now
                    
                    response_time = time.time() - start_time
                    times.append(response_time)
                    
                    assert response.status_code == 200, f"API error for {path}: {response.status_code}"
                
                response_times[path] = {
                    "mean": statistics.mean(times),
                    "max": max(times),
                    "min": min(times)
                }
                
                print(f"   {path}: {response_times[path]['mean']:.3f}s avg, "
                      f"{response_times[path]['max']:.3f}s max")
            
            # Performance assertions
            for path, times in response_times.items():
                assert times["mean"] < 1.0, f"API response too slow for {path}: {times['mean']:.3f}s"
                assert times["max"] < 2.0, f"API max response too slow for {path}: {times['max']:.3f}s"
            
            print("✅ API response time benchmark complete")
            
        finally:
            generator.cleanup_all_data()
    
    def test_concurrent_api_load_handling(self, temp_demo_dir):
        """
        Test API performance under concurrent load
        Requirements: 6.2
        """
        config = DemoConfig(
            num_users=8,
            conversations_per_user=4,
            output_directory=temp_demo_dir
        )
        
        service_config = ServiceConfig(
            mock_api_port=8905,
            auto_open_browser=False,
            processing_delay_ms=10
        )
        
        config_manager = ConfigurationManager()
        config_manager.update_demo_config(config)
        config_manager.update_service_config(service_config)
        generator = DemoDataGenerator(config_manager)
        
        # Setup
        result = generator.generate_all_data(config)
        assert result.success, "Data generation failed"
        
        launch_result = generator.launch_complete_demo(auto_browser=False, config=service_config)
        assert launch_result["success"], "Service launch failed"
        
        try:
            api_url = launch_result["urls"]["api"]
            time.sleep(2)
            
            print("🧪 Testing concurrent API load handling...")
            
            def make_api_request(request_id: int) -> Dict[str, Any]:
                """Make a single API request and return timing info"""
                start_time = time.time()
                try:
                    response = requests.get(f"{api_url}/api/users", timeout=15)
                    response_time = time.time() - start_time
                    
                    return {
                        "request_id": request_id,
                        "success": response.status_code == 200,
                        "response_time": response_time,
                        "status_code": response.status_code
                    }
                except Exception as e:
                    return {
                        "request_id": request_id,
                        "success": False,
                        "response_time": time.time() - start_time,
                        "error": str(e)
                    }
            
            # Test with concurrent requests
            concurrent_requests = 10
            
            with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                futures = [executor.submit(make_api_request, i) for i in range(concurrent_requests)]
                results = [future.result() for future in as_completed(futures)]
            
            # Analyze results
            successful_requests = [r for r in results if r["success"]]
            failed_requests = [r for r in results if not r["success"]]
            
            success_rate = len(successful_requests) / len(results)
            
            if successful_requests:
                response_times = [r["response_time"] for r in successful_requests]
                mean_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
            else:
                mean_response_time = float('inf')
                max_response_time = float('inf')
            
            print(f"   Concurrent requests: {concurrent_requests}")
            print(f"   Success rate: {success_rate:.2%}")
            print(f"   Mean response time: {mean_response_time:.3f}s")
            print(f"   Max response time: {max_response_time:.3f}s")
            
            # Performance assertions
            assert success_rate >= 0.9, f"Success rate too low: {success_rate:.2%}"
            assert mean_response_time < 3.0, f"Mean response time too slow under load: {mean_response_time:.3f}s"
            
            if failed_requests:
                print(f"   Failed requests: {len(failed_requests)}")
                for req in failed_requests[:3]:  # Show first few failures
                    print(f"     Request {req['request_id']}: {req.get('error', 'Unknown error')}")
            
            print("✅ Concurrent load handling test complete")
            
        finally:
            generator.cleanup_all_data()


class TestFrontendResponsiveness:
    """Test frontend responsiveness with generated data"""
    
    def test_frontend_loading_performance(self):
        """
        Test frontend loading performance with different data volumes
        Requirements: 6.2
        """
        # This test would ideally use a headless browser like Selenium
        # For now, we'll test the API endpoints that the frontend would use
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = DemoConfig(
                num_users=15,
                conversations_per_user=6,
                output_directory=temp_dir
            )
            
            service_config = ServiceConfig(
                mock_api_port=8906,
                auto_open_browser=False
            )
            
            config_manager = ConfigurationManager()
            config_manager.update_demo_config(config)
            config_manager.update_service_config(service_config)
            generator = DemoDataGenerator(config_manager)
            
            # Setup
            result = generator.generate_all_data(config)
            assert result.success, "Data generation failed"
            
            launch_result = generator.launch_complete_demo(auto_browser=False, config=service_config)
            assert launch_result["success"], "Service launch failed"
            
            try:
                api_url = launch_result["urls"]["api"]
                time.sleep(2)
                
                print("🧪 Testing frontend data loading performance...")
                
                # Test endpoints that frontend would typically call on load
                frontend_endpoints = [
                    "/api/users",
                    "/api/cultural/patterns",
                    "/health"
                ]
                
                total_load_time = 0
                
                for endpoint in frontend_endpoints:
                    start_time = time.time()
                    response = requests.get(f"{api_url}{endpoint}", timeout=10)
                    load_time = time.time() - start_time
                    total_load_time += load_time
                    
                    assert response.status_code == 200, f"Frontend endpoint failed: {endpoint}"
                    
                    # Check response size (frontend needs to handle this)
                    response_size = len(response.content)
                    print(f"   {endpoint}: {load_time:.3f}s, {response_size} bytes")
                    
                    # Performance assertions
                    assert load_time < 2.0, f"Endpoint too slow for frontend: {endpoint} ({load_time:.3f}s)"
                
                print(f"   Total initial load time: {total_load_time:.3f}s")
                
                # Total load time should be reasonable for frontend
                assert total_load_time < 5.0, f"Total frontend load time too slow: {total_load_time:.3f}s"
                
                print("✅ Frontend loading performance test complete")
                
            finally:
                generator.cleanup_all_data()
    
    def test_data_volume_impact_on_responsiveness(self):
        """
        Test how data volume affects system responsiveness
        Requirements: 6.2
        """
        print("🧪 Testing data volume impact on responsiveness...")
        
        volume_configs = [
            {"users": 5, "conversations": 3, "name": "small"},
            {"users": 15, "conversations": 5, "name": "medium"},
            {"users": 25, "conversations": 7, "name": "large"}
        ]
        
        responsiveness_results = []
        
        for i, volume_config in enumerate(volume_configs):
            with tempfile.TemporaryDirectory() as temp_dir:
                config = DemoConfig(
                    num_users=volume_config["users"],
                    conversations_per_user=volume_config["conversations"],
                    output_directory=temp_dir
                )
                
                service_config = ServiceConfig(
                    mock_api_port=8907 + i,  # Different port for each test
                    auto_open_browser=False
                )
                
                config_manager = ConfigurationManager()
                config_manager.update_demo_config(config)
                config_manager.update_service_config(service_config)
                generator = DemoDataGenerator(config_manager)
                
                # Generate data and launch services
                result = generator.generate_all_data(config)
                assert result.success, f"Data generation failed for {volume_config['name']}"
                
                launch_result = generator.launch_complete_demo(auto_browser=False, config=service_config)
                assert launch_result["success"], f"Service launch failed for {volume_config['name']}"
                
                try:
                    api_url = launch_result["urls"]["api"]
                    time.sleep(2)
                    
                    # Test responsiveness with this data volume
                    start_time = time.time()
                    response = requests.get(f"{api_url}/api/users", timeout=15)
                    response_time = time.time() - start_time
                    
                    assert response.status_code == 200, f"API failed for {volume_config['name']}"
                    
                    response_data = response.json()
                    data_size = len(json.dumps(response_data))
                    
                    responsiveness_results.append({
                        "name": volume_config["name"],
                        "users": volume_config["users"],
                        "conversations": volume_config["conversations"],
                        "response_time": response_time,
                        "data_size": data_size
                    })
                    
                    print(f"   {volume_config['name']}: {response_time:.3f}s, {data_size} bytes")
                    
                finally:
                    generator.cleanup_all_data()
        
        # Analyze responsiveness scaling
        small_time = responsiveness_results[0]["response_time"]
        large_time = responsiveness_results[-1]["response_time"]
        
        # Response time shouldn't increase dramatically with data volume
        time_ratio = large_time / small_time if small_time > 0 else float('inf')
        assert time_ratio < 3.0, f"Responsiveness degrades too much with data volume: {time_ratio:.2f}x"
        
        print(f"✅ Data volume impact test complete. Time ratio: {time_ratio:.2f}x")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s", "--tb=short"])