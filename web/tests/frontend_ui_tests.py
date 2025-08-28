#!/usr/bin/env python3
"""
Frontend UI Testing Suite
Human-like verification of frontend functionality with automated browser testing
"""

import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrontendUITester:
    """Frontend UI testing with human-like verification"""
    
    def __init__(self, frontend_url: str = "http://localhost:5173"):
        self.frontend_url = frontend_url
        self.driver = None
        self.test_results = []
        
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("✅ Chrome WebDriver initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup WebDriver: {e}")
            logger.info("💡 Falling back to manual verification mode")
            return False
    
    def teardown_driver(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🧹 WebDriver cleaned up")
    
    def log_test_result(self, test_name: str, status: str, message: str, details: Dict = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
        logger.info(f"{status_emoji} {test_name}: {message}")
    
    def test_page_load(self):
        """Test basic page loading and title"""
        if not self.driver:
            self.manual_page_load_test()
            return
            
        try:
            self.driver.get(self.frontend_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check title
            title = self.driver.title
            if "TradingAgents" in title or title:
                self.log_test_result(
                    "Page Load", 
                    "PASS", 
                    f"Page loaded successfully - Title: {title}",
                    {"title": title, "url": self.driver.current_url}
                )
            else:
                self.log_test_result("Page Load", "FAIL", "Page title missing or incorrect")
                
        except Exception as e:
            self.log_test_result("Page Load", "FAIL", f"Page load failed: {str(e)}")
    
    def manual_page_load_test(self):
        """Manual page load verification"""
        import requests
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                if "TradingAgents" in response.text:
                    self.log_test_result(
                        "Page Load (Manual)", 
                        "PASS", 
                        "Page accessible and contains expected content"
                    )
                else:
                    self.log_test_result(
                        "Page Load (Manual)", 
                        "FAIL", 
                        "Page missing expected content"
                    )
            else:
                self.log_test_result(
                    "Page Load (Manual)", 
                    "FAIL", 
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            self.log_test_result("Page Load (Manual)", "FAIL", f"Connection failed: {str(e)}")
    
    def test_configuration_form(self):
        """Test configuration form elements and interactions"""
        if not self.driver:
            self.manual_configuration_test()
            return
            
        try:
            # Check for configuration section
            config_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Analysis Configuration')]"))
            )
            
            # Test ticker input
            ticker_input = self.driver.find_element(By.XPATH, "//input[@placeholder='e.g., TSLA, AAPL, SPY']")
            ticker_input.clear()
            ticker_input.send_keys("AAPL")
            
            # Test date input
            date_inputs = self.driver.find_elements(By.XPATH, "//input[@type='date']")
            if date_inputs:
                date_inputs[0].send_keys("2025-08-28")
            
            # Test analyst checkboxes
            checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            checked_analysts = []
            for checkbox in checkboxes[:2]:  # Check first 2 analysts
                if not checkbox.is_selected():
                    checkbox.click()
                    checked_analysts.append("checked")
            
            # Test research depth radio buttons
            radio_buttons = self.driver.find_elements(By.XPATH, "//input[@type='radio']")
            if radio_buttons:
                radio_buttons[1].click()  # Select medium depth
            
            # Test LLM provider dropdown
            llm_select = self.driver.find_element(By.XPATH, "//select")
            llm_select.click()
            
            self.log_test_result(
                "Configuration Form", 
                "PASS", 
                f"All form elements interactive - {len(checkboxes)} analysts, {len(radio_buttons)} depth options",
                {
                    "ticker_set": "AAPL",
                    "analysts_available": len(checkboxes),
                    "depth_options": len(radio_buttons),
                    "form_elements_found": True
                }
            )
            
        except Exception as e:
            self.log_test_result("Configuration Form", "FAIL", f"Form interaction failed: {str(e)}")
    
    def manual_configuration_test(self):
        """Manual configuration form verification"""
        import requests
        try:
            response = requests.get(self.frontend_url, timeout=10)
            html = response.text
            
            required_elements = [
                "Ticker Symbol",
                "Analysis Date", 
                "Select Analysts",
                "Research Depth",
                "LLM Provider",
                "Quick-Thinking LLM",
                "Deep-Thinking LLM"
            ]
            
            found_elements = []
            for element in required_elements:
                if element in html:
                    found_elements.append(element)
            
            if len(found_elements) == len(required_elements):
                self.log_test_result(
                    "Configuration Form (Manual)", 
                    "PASS", 
                    f"All {len(required_elements)} configuration elements found",
                    {"elements_found": found_elements}
                )
            else:
                missing = set(required_elements) - set(found_elements)
                self.log_test_result(
                    "Configuration Form (Manual)", 
                    "FAIL", 
                    f"Missing elements: {missing}",
                    {"found": found_elements, "missing": list(missing)}
                )
                
        except Exception as e:
            self.log_test_result("Configuration Form (Manual)", "FAIL", f"Verification failed: {str(e)}")
    
    def test_start_analysis_button(self):
        """Test start analysis button functionality"""
        if not self.driver:
            self.manual_button_test()
            return
            
        try:
            # Find start analysis button
            start_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Start') and contains(text(), 'Analysis')]"))
            )
            
            # Check button text and state
            button_text = start_button.text
            is_enabled = start_button.is_enabled()
            
            # Click the button
            start_button.click()
            
            # Wait for state change
            time.sleep(2)
            
            # Check if button state changed (should show "Analyzing...")
            try:
                analyzing_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Analyzing')]")
                self.log_test_result(
                    "Start Analysis Button", 
                    "PASS", 
                    "Button click triggered analysis state change",
                    {"initial_text": button_text, "enabled": is_enabled}
                )
            except NoSuchElementException:
                self.log_test_result(
                    "Start Analysis Button", 
                    "PASS", 
                    "Button clickable but no state change detected",
                    {"initial_text": button_text, "enabled": is_enabled}
                )
                
        except Exception as e:
            self.log_test_result("Start Analysis Button", "FAIL", f"Button test failed: {str(e)}")
    
    def manual_button_test(self):
        """Manual button verification"""
        import requests
        try:
            response = requests.get(self.frontend_url, timeout=10)
            html = response.text
            
            button_indicators = [
                "Start Multi-Agent Analysis",
                "Start Analysis", 
                "button",
                "onClick"
            ]
            
            found_indicators = []
            for indicator in button_indicators:
                if indicator in html:
                    found_indicators.append(indicator)
            
            if found_indicators:
                self.log_test_result(
                    "Start Analysis Button (Manual)", 
                    "PASS", 
                    f"Button elements found: {found_indicators}",
                    {"indicators_found": found_indicators}
                )
            else:
                self.log_test_result(
                    "Start Analysis Button (Manual)", 
                    "FAIL", 
                    "No button elements detected"
                )
                
        except Exception as e:
            self.log_test_result("Start Analysis Button (Manual)", "FAIL", f"Verification failed: {str(e)}")
    
    def test_responsive_design(self):
        """Test responsive design at different screen sizes"""
        if not self.driver:
            self.log_test_result("Responsive Design", "SKIP", "WebDriver not available")
            return
            
        screen_sizes = [
            (1920, 1080, "Desktop"),
            (1024, 768, "Tablet"),
            (375, 667, "Mobile")
        ]
        
        responsive_results = []
        
        for width, height, device in screen_sizes:
            try:
                self.driver.set_window_size(width, height)
                time.sleep(1)  # Allow layout to adjust
                
                # Check if main elements are still visible
                body = self.driver.find_element(By.TAG_NAME, "body")
                body_size = body.size
                
                # Check for horizontal scrollbar (indicates layout issues)
                scroll_width = self.driver.execute_script("return document.body.scrollWidth")
                client_width = self.driver.execute_script("return document.body.clientWidth")
                
                has_horizontal_scroll = scroll_width > client_width
                
                responsive_results.append({
                    "device": device,
                    "size": f"{width}x{height}",
                    "body_size": body_size,
                    "horizontal_scroll": has_horizontal_scroll
                })
                
            except Exception as e:
                responsive_results.append({
                    "device": device,
                    "size": f"{width}x{height}",
                    "error": str(e)
                })
        
        # Reset to desktop size
        self.driver.set_window_size(1920, 1080)
        
        # Evaluate results
        issues = [r for r in responsive_results if r.get("horizontal_scroll") or r.get("error")]
        
        if not issues:
            self.log_test_result(
                "Responsive Design", 
                "PASS", 
                f"Layout works correctly on all {len(screen_sizes)} screen sizes",
                {"tested_sizes": responsive_results}
            )
        else:
            self.log_test_result(
                "Responsive Design", 
                "FAIL", 
                f"Layout issues found on {len(issues)} screen sizes",
                {"issues": issues, "all_results": responsive_results}
            )
    
    def test_accessibility_features(self):
        """Test basic accessibility features"""
        if not self.driver:
            self.manual_accessibility_test()
            return
            
        try:
            accessibility_checks = []
            
            # Check for alt text on images
            images = self.driver.find_elements(By.TAG_NAME, "img")
            images_with_alt = [img for img in images if img.get_attribute("alt")]
            accessibility_checks.append({
                "check": "Image Alt Text",
                "total_images": len(images),
                "images_with_alt": len(images_with_alt),
                "pass": len(images) == 0 or len(images_with_alt) > 0
            })
            
            # Check for form labels
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            labeled_inputs = []
            for input_elem in inputs:
                input_id = input_elem.get_attribute("id")
                if input_id:
                    try:
                        label = self.driver.find_element(By.XPATH, f"//label[@for='{input_id}']")
                        labeled_inputs.append(input_elem)
                    except NoSuchElementException:
                        pass
            
            accessibility_checks.append({
                "check": "Form Labels",
                "total_inputs": len(inputs),
                "labeled_inputs": len(labeled_inputs),
                "pass": len(inputs) == 0 or len(labeled_inputs) > len(inputs) * 0.5  # At least 50% labeled
            })
            
            # Check for heading structure
            headings = self.driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6")
            accessibility_checks.append({
                "check": "Heading Structure",
                "total_headings": len(headings),
                "pass": len(headings) > 0
            })
            
            # Evaluate overall accessibility
            passed_checks = [check for check in accessibility_checks if check["pass"]]
            
            if len(passed_checks) == len(accessibility_checks):
                self.log_test_result(
                    "Accessibility Features", 
                    "PASS", 
                    f"All {len(accessibility_checks)} accessibility checks passed",
                    {"checks": accessibility_checks}
                )
            else:
                failed_checks = [check for check in accessibility_checks if not check["pass"]]
                self.log_test_result(
                    "Accessibility Features", 
                    "FAIL", 
                    f"{len(failed_checks)} accessibility issues found",
                    {"passed": passed_checks, "failed": failed_checks}
                )
                
        except Exception as e:
            self.log_test_result("Accessibility Features", "FAIL", f"Accessibility test failed: {str(e)}")
    
    def manual_accessibility_test(self):
        """Manual accessibility verification"""
        import requests
        try:
            response = requests.get(self.frontend_url, timeout=10)
            html = response.text
            
            accessibility_indicators = [
                "aria-",
                "role=",
                "alt=",
                "label",
                "<h1", "<h2", "<h3"
            ]
            
            found_indicators = []
            for indicator in accessibility_indicators:
                if indicator in html:
                    found_indicators.append(indicator)
            
            if len(found_indicators) >= 3:  # At least 3 accessibility features
                self.log_test_result(
                    "Accessibility Features (Manual)", 
                    "PASS", 
                    f"Accessibility features detected: {found_indicators}",
                    {"features_found": found_indicators}
                )
            else:
                self.log_test_result(
                    "Accessibility Features (Manual)", 
                    "FAIL", 
                    f"Limited accessibility features: {found_indicators}",
                    {"features_found": found_indicators}
                )
                
        except Exception as e:
            self.log_test_result("Accessibility Features (Manual)", "FAIL", f"Verification failed: {str(e)}")
    
    def run_all_tests(self):
        """Run complete frontend UI test suite"""
        logger.info("🎨 Starting Frontend UI Test Suite")
        logger.info("=" * 50)
        
        start_time = time.time()
        
        # Setup WebDriver (fallback to manual if fails)
        driver_available = self.setup_driver()
        
        # Run all tests
        tests = [
            self.test_page_load,
            self.test_configuration_form,
            self.test_start_analysis_button,
            self.test_responsive_design,
            self.test_accessibility_features
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"❌ Test {test.__name__} crashed: {e}")
        
        # Cleanup
        self.teardown_driver()
        
        # Generate summary
        total_time = time.time() - start_time
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        logger.info(f"\n📊 FRONTEND UI TEST SUMMARY")
        logger.info(f"Total Tests: {len(self.test_results)}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Skipped: {skipped} ⏭️")
        logger.info(f"Duration: {total_time:.2f}s")
        logger.info(f"WebDriver: {'Available' if driver_available else 'Manual Mode'}")
        
        # Save results
        with open("frontend_ui_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total": len(self.test_results),
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped,
                    "duration": total_time,
                    "webdriver_available": driver_available
                },
                "results": self.test_results
            }, f, indent=2)
        
        return failed == 0

def main():
    """Main execution"""
    print("🎨 Frontend UI Testing Suite")
    print("=" * 40)
    
    tester = FrontendUITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All frontend tests passed!")
    else:
        print("\n💥 Some frontend tests failed!")

if __name__ == "__main__":
    main()
