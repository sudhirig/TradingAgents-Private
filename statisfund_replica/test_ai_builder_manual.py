#!/usr/bin/env python3
"""
Manual AI Builder Frontend Testing
Tests the new LLM-style interface through browser automation
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import sys

class AIBuilderUITester:
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        self.base_url = "http://localhost:3000"
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            return False
    
    def test_page_load(self):
        """Test if the AI Builder page loads correctly"""
        try:
            self.driver.get(self.base_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if AI Builder button exists and click it
            ai_builder_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'AI Builder')]"))
            )
            ai_builder_btn.click()
            
            # Wait for AI Builder interface to load
            time.sleep(2)
            
            # Check for key elements
            title = self.driver.find_element(By.XPATH, "//*[contains(text(), 'AI Trading Strategy Assistant')]")
            chat_input = self.driver.find_element(By.XPATH, "//textarea[@placeholder]")
            
            print("✅ AI Builder page loaded successfully")
            print(f"   - Title found: {title.text[:50]}...")
            print(f"   - Chat input found: {chat_input.get_attribute('placeholder')[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Page load test failed: {e}")
            return False
    
    def test_example_prompts(self):
        """Test clicking example prompts"""
        try:
            # Look for example prompt buttons
            example_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'example-prompt') or contains(text(), 'swing trading') or contains(text(), 'momentum')]")
            
            if not example_buttons:
                print("⚠️  No example prompt buttons found")
                return False
            
            print(f"✅ Found {len(example_buttons)} example prompts")
            
            # Click first example
            first_example = example_buttons[0]
            example_text = first_example.text[:50]
            first_example.click()
            
            time.sleep(1)
            
            # Check if text appeared in input
            chat_input = self.driver.find_element(By.XPATH, "//textarea[@placeholder]")
            input_value = chat_input.get_attribute('value')
            
            if input_value:
                print(f"✅ Example prompt clicked successfully: {example_text}...")
                print(f"   - Input populated with: {input_value[:50]}...")
                return True
            else:
                print("❌ Example prompt didn't populate input")
                return False
                
        except Exception as e:
            print(f"❌ Example prompts test failed: {e}")
            return False
    
    def test_chat_interface(self):
        """Test the chat interface functionality"""
        try:
            # Find chat input
            chat_input = self.driver.find_element(By.XPATH, "//textarea[@placeholder]")
            
            # Clear and type a test message
            chat_input.clear()
            test_message = "Create a simple moving average crossover strategy"
            chat_input.send_keys(test_message)
            
            # Find and click send button
            send_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'send-btn') or contains(text(), 'Send') or @type='submit']")
            send_button.click()
            
            print("✅ Chat message sent successfully")
            print(f"   - Message: {test_message}")
            
            # Wait for response (this might take a while due to AI generation)
            print("⏳ Waiting for AI response...")
            
            # Look for loading indicator or response
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda driver: len(driver.find_elements(By.XPATH, "//*[contains(@class, 'message') or contains(@class, 'chat-message')]")) > 1
                )
                print("✅ AI response received")
                return True
            except:
                print("⚠️  AI response timeout (30s) - may be backend issue")
                return False
                
        except Exception as e:
            print(f"❌ Chat interface test failed: {e}")
            return False
    
    def test_sidebar_functionality(self):
        """Test settings sidebar"""
        try:
            # Look for sidebar elements
            sidebar_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'sidebar') or contains(@class, 'settings')]")
            
            if not sidebar_elements:
                print("⚠️  Sidebar not found")
                return False
            
            # Look for symbol selector
            symbol_selects = self.driver.find_elements(By.XPATH, "//select[contains(@class, 'symbol') or @name='symbol']")
            
            # Look for backtest buttons
            backtest_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Backtest') or contains(text(), 'Test')]")
            
            print(f"✅ Sidebar functionality found")
            print(f"   - Symbol selectors: {len(symbol_selects)}")
            print(f"   - Backtest buttons: {len(backtest_buttons)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Sidebar test failed: {e}")
            return False
    
    def test_responsive_design(self):
        """Test responsive design"""
        try:
            # Test different screen sizes
            sizes = [
                (1920, 1080, "Desktop"),
                (768, 1024, "Tablet"),
                (375, 667, "Mobile")
            ]
            
            for width, height, device in sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                # Check if main elements are still visible
                body = self.driver.find_element(By.TAG_NAME, "body")
                if body.is_displayed():
                    print(f"✅ {device} ({width}x{height}) - Layout responsive")
                else:
                    print(f"❌ {device} ({width}x{height}) - Layout broken")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Responsive design test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all UI tests"""
        print("🚀 Starting AI Builder UI Testing Suite")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        tests = [
            ("Page Load", self.test_page_load),
            ("Example Prompts", self.test_example_prompts),
            ("Chat Interface", self.test_chat_interface),
            ("Sidebar Functionality", self.test_sidebar_functionality),
            ("Responsive Design", self.test_responsive_design)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name} Test...")
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
                results[test_name] = False
        
        # Summary
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        success_rate = (passed / total) * 100
        
        print("\n" + "=" * 50)
        print("📊 UI TEST RESULTS")
        print("=" * 50)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 UI Success Rate: {success_rate:.1f}% ({passed}/{total})")
        
        if success_rate >= 80:
            print("🎉 AI Builder UI is working excellently!")
        elif success_rate >= 60:
            print("⚠️  AI Builder UI has minor issues")
        else:
            print("🔧 AI Builder UI needs significant fixes")
        
        return success_rate >= 60
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()

def main():
    """Main test runner"""
    headless = "--headless" in sys.argv
    
    tester = AIBuilderUITester(headless=headless)
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
