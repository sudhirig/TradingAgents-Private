#!/usr/bin/env python3
"""
Frontend UI Testing Script for Statis Fund Replica
Tests the complete user flow from strategy generation to backtesting
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

class FrontendUITester:
    def __init__(self, frontend_url="http://localhost:3000", backend_url="http://localhost:8000"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.driver = None
        self.test_results = []
        
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            print("💡 Install ChromeDriver: brew install chromedriver")
            return False
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    def check_backend_health(self):
        """Verify backend is running"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            success = response.status_code == 200
            self.log_test("Backend Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_page_load(self):
        """Test if frontend loads correctly"""
        try:
            self.driver.get(self.frontend_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check for key elements
            title = self.driver.title
            success = "Statis Fund" in title or len(title) > 0
            self.log_test("Frontend Page Load", success, f"Title: {title}")
            return success
            
        except Exception as e:
            self.log_test("Frontend Page Load", False, f"Exception: {str(e)}")
            return False
    
    def test_strategy_generation_ui(self):
        """Test strategy generation through UI"""
        try:
            # Find strategy description input
            description_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, input[type='text']"))
            )
            
            # Enter strategy description
            test_description = "Simple moving average crossover strategy for AAPL with RSI confirmation"
            description_input.clear()
            description_input.send_keys(test_description)
            
            # Find and click generate button
            generate_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate') or contains(text(), 'Create')]")
            generate_button.click()
            
            # Wait for code to appear
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "pre, code, .code-display"))
            )
            
            # Check if code was generated
            code_elements = self.driver.find_elements(By.CSS_SELECTOR, "pre, code, .code-display")
            generated_code = ""
            for element in code_elements:
                text = element.text
                if "class" in text and "Strategy" in text:
                    generated_code = text
                    break
            
            success = len(generated_code) > 100 and "bt.Strategy" in generated_code
            self.log_test("Strategy Generation UI", success, f"Generated {len(generated_code)} chars")
            return success, generated_code
            
        except Exception as e:
            self.log_test("Strategy Generation UI", False, f"Exception: {str(e)}")
            return False, ""
    
    def test_backtest_ui(self):
        """Test backtesting through UI"""
        try:
            # Look for backtest button
            backtest_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Backtest') or contains(text(), 'Run')]")
            
            if not backtest_buttons:
                self.log_test("Backtest UI", False, "No backtest button found")
                return False
            
            # Click first backtest button
            backtest_buttons[0].click()
            
            # Wait for results
            WebDriverWait(self.driver, 60).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".results, .performance, .metrics")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Return') or contains(text(), 'Sharpe')]"))
                )
            )
            
            # Check for performance metrics
            page_text = self.driver.page_source.lower()
            has_metrics = any(metric in page_text for metric in ["return", "sharpe", "drawdown", "trades"])
            
            success = has_metrics
            self.log_test("Backtest UI", success, "Found performance metrics" if success else "No metrics found")
            return success
            
        except TimeoutException:
            self.log_test("Backtest UI", False, "Timeout waiting for results")
            return False
        except Exception as e:
            self.log_test("Backtest UI", False, f"Exception: {str(e)}")
            return False
    
    def test_advanced_backtest_ui(self):
        """Test advanced backtesting through UI"""
        try:
            # Look for advanced backtest button
            advanced_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Advanced') or contains(text(), 'Enhanced')]")
            
            if not advanced_buttons:
                self.log_test("Advanced Backtest UI", False, "No advanced backtest button found")
                return False
            
            # Click advanced backtest button
            advanced_buttons[0].click()
            
            # Wait for advanced results
            WebDriverWait(self.driver, 60).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sortino') or contains(text(), 'Calmar')]")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".advanced-metrics, .enhanced-results"))
                )
            )
            
            # Check for advanced metrics
            page_text = self.driver.page_source.lower()
            has_advanced_metrics = any(metric in page_text for metric in ["sortino", "calmar", "sqn", "vwr"])
            
            success = has_advanced_metrics
            self.log_test("Advanced Backtest UI", success, "Found advanced metrics" if success else "No advanced metrics found")
            return success
            
        except TimeoutException:
            self.log_test("Advanced Backtest UI", False, "Timeout waiting for advanced results")
            return False
        except Exception as e:
            self.log_test("Advanced Backtest UI", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_ui(self):
        """Test UI error handling"""
        try:
            # Test with invalid input
            description_input = self.driver.find_element(By.CSS_SELECTOR, "textarea, input[type='text']")
            description_input.clear()
            description_input.send_keys("")  # Empty description
            
            generate_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate') or contains(text(), 'Create')]")
            generate_button.click()
            
            # Wait for error message
            time.sleep(3)
            page_text = self.driver.page_source.lower()
            has_error = any(error in page_text for error in ["error", "required", "invalid", "failed"])
            
            success = has_error
            self.log_test("Error Handling UI", success, "Found error message" if success else "No error handling")
            return success
            
        except Exception as e:
            self.log_test("Error Handling UI", False, f"Exception: {str(e)}")
            return False
    
    def test_responsive_design(self):
        """Test responsive design"""
        try:
            # Test mobile viewport
            self.driver.set_window_size(375, 667)  # iPhone size
            time.sleep(2)
            
            # Check if elements are still accessible
            body = self.driver.find_element(By.TAG_NAME, "body")
            body_width = body.size['width']
            
            # Test tablet viewport
            self.driver.set_window_size(768, 1024)  # iPad size
            time.sleep(2)
            
            # Reset to desktop
            self.driver.set_window_size(1920, 1080)
            time.sleep(2)
            
            success = body_width > 0  # Basic check that page renders
            self.log_test("Responsive Design", success, f"Mobile width: {body_width}px")
            return success
            
        except Exception as e:
            self.log_test("Responsive Design", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run complete UI testing suite"""
        print("🚀 Starting Frontend UI Testing Suite")
        print(f"📍 Frontend: {self.frontend_url}")
        print(f"📍 Backend: {self.backend_url}")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_backend_health():
            print("❌ Backend not available, skipping UI tests")
            return
        
        if not self.setup_driver():
            print("❌ WebDriver setup failed, skipping UI tests")
            return
        
        try:
            # Phase 1: Basic functionality
            print("\n📱 Phase 1: Basic UI Tests")
            if not self.test_page_load():
                return
            
            # Phase 2: Core workflow
            print("\n🧠 Phase 2: Strategy Generation Workflow")
            success, code = self.test_strategy_generation_ui()
            if success:
                print("\n📊 Phase 3: Backtesting Workflow")
                self.test_backtest_ui()
                self.test_advanced_backtest_ui()
            
            # Phase 3: Edge cases
            print("\n🔧 Phase 4: Error Handling & UX")
            self.test_error_handling_ui()
            self.test_responsive_design()
            
        finally:
            if self.driver:
                self.driver.quit()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate UI test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("📋 UI TEST SUMMARY REPORT")
        print("=" * 60)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test_name']}: {result['details']}")
        
        # Save results
        with open("ui_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"💾 UI test results saved to: ui_test_results.json")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Frontend UI Testing Suite")
    parser.add_argument("--frontend", default="http://localhost:3000", help="Frontend URL")
    parser.add_argument("--backend", default="http://localhost:8000", help="Backend URL")
    args = parser.parse_args()
    
    tester = FrontendUITester(args.frontend, args.backend)
    tester.run_all_tests()
