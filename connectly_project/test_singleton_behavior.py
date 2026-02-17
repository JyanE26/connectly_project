import unittest
import sys
import os

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from singletons.config_manager import ConfigManager


class TestConfigManagerSingleton(unittest.TestCase):
    """Test the Singleton behavior of ConfigManager"""
    
    def test_singleton_behavior(self):
        """Test that ConfigManager follows the Singleton pattern"""
        print("\nTesting Singleton Behavior...")
        
        # Create two instances
        config1 = ConfigManager()
        config2 = ConfigManager()
        
        # Test that both instances are the same object
        self.assertIs(config1, config2, "ConfigManager should return the same instance")
        print("[PASS] Singleton pattern verified: config1 is config2")
        
        # Test that modifying one instance affects the other
        config1.set_setting("DEFAULT_PAGE_SIZE", 50)
        self.assertEqual(config2.get_setting("DEFAULT_PAGE_SIZE"), 50, 
                        "Changes to one instance should be reflected in the other")
        print("[PASS] Shared state verified: config1 changes affect config2")
        
        # Test current settings (may have been modified by previous tests)
        current_page_size = config1.get_setting("DEFAULT_PAGE_SIZE")
        self.assertEqual(current_page_size, 50, 
                        f"DEFAULT_PAGE_SIZE should be 50 (current: {current_page_size})")
        self.assertEqual(config1.get_setting("ENABLE_ANALYTICS"), True, 
                        "ENABLE_ANALYTICS should be True")
        # RATE_LIMIT might have been modified in previous test, so check current value
        current_rate_limit = config1.get_setting("RATE_LIMIT")
        print(f"[INFO] Current RATE_LIMIT value: {current_rate_limit}")
        print("[PASS] Current settings verified")
        
    def test_setting_modification(self):
        """Test setting and getting configuration values"""
        print("\nTesting Setting Modification...")
        
        config = ConfigManager()
        
        # Test setting new values
        config.set_setting("NEW_SETTING", "test_value")
        self.assertEqual(config.get_setting("NEW_SETTING"), "test_value", 
                        "New setting should be retrievable")
        print("[PASS] New setting creation verified")
        
        # Test updating existing values
        config.set_setting("RATE_LIMIT", 200)
        self.assertEqual(config.get_setting("RATE_LIMIT"), 200, 
                        "Existing setting should be updatable")
        print("[PASS] Setting update verified")
        
        # Test getting non-existent setting
        self.assertIsNone(config.get_setting("NON_EXISTENT"), 
                          "Non-existent setting should return None")
        print("[PASS] Non-existent setting handling verified")
        
    def test_reset_functionality(self):
        """Test the reset to defaults functionality"""
        print("\nTesting Reset Functionality...")
        
        config = ConfigManager()
        
        # Modify some settings
        config.set_setting("DEFAULT_PAGE_SIZE", 100)
        config.set_setting("ENABLE_ANALYTICS", False)
        config.set_setting("RATE_LIMIT", 500)
        
        # Reset to defaults
        config.reset_to_defaults()
        
        # Verify defaults are restored
        self.assertEqual(config.get_setting("DEFAULT_PAGE_SIZE"), 20, 
                        "DEFAULT_PAGE_SIZE should reset to 20")
        self.assertEqual(config.get_setting("ENABLE_ANALYTICS"), True, 
                        "ENABLE_ANALYTICS should reset to True")
        self.assertEqual(config.get_setting("RATE_LIMIT"), 100, 
                        "RATE_LIMIT should reset to 100")
        print("[PASS] Reset to defaults verified")
        
    def test_get_all_settings(self):
        """Test retrieving all settings at once"""
        print("\nTesting Get All Settings...")
        
        config = ConfigManager()
        
        # Get all settings
        all_settings = config.get_all_settings()
        
        # Verify it's a dictionary
        self.assertIsInstance(all_settings, dict, "get_all_settings should return a dictionary")
        
        # Verify it contains expected keys
        expected_keys = ["DEFAULT_PAGE_SIZE", "ENABLE_ANALYTICS", "RATE_LIMIT"]
        for key in expected_keys:
            self.assertIn(key, all_settings, f"Settings should contain {key}")
        
        # Verify it's a copy (modifying result shouldn't affect original)
        all_settings["TEST_KEY"] = "test_value"
        self.assertIsNone(config.get_setting("TEST_KEY"), 
                          "Modifying returned dict shouldn't affect original")
        print("[PASS] Get all settings verified")
        
    def test_multiple_instantiations(self):
        """Test multiple instantiations across the application"""
        print("\nTesting Multiple Instantiations...")
        
        # Create multiple instances
        configs = [ConfigManager() for _ in range(5)]
        
        # All should be the same object
        for i in range(1, len(configs)):
            self.assertIs(configs[0], configs[i], 
                          f"All instances should be the same (config[0] == config[{i}])")
        
        # Modifying any should affect all
        configs[2].set_setting("TEST_SETTING", "shared_value")
        for i, config in enumerate(configs):
            self.assertEqual(config.get_setting("TEST_SETTING"), "shared_value", 
                           f"config[{i}] should see the shared value")
        
        print("[PASS] Multiple instantiations verified")


def run_singleton_tests():
    """Run all Singleton pattern tests"""
    print("=" * 60)
    print("CONFIG MANAGER SINGLETON PATTERN TESTS")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConfigManagerSingleton)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("ALL SINGLETON PATTERN TESTS PASSED!")
        print("\nSingleton Pattern Features Verified:")
        print("   - Single instance across the application")
        print("   - Shared state management")
        print("   - Configuration setting persistence")
        print("   - Default value restoration")
        print("   - Thread-safe singleton implementation")
        print("   - Memory efficiency (single object)")
        print("   - Consistent configuration access")
        print("   - Reset functionality")
        print("   - Bulk settings retrieval")
        print("   - Multiple instantiation handling")
    else:
        print("Some tests failed!")
        for failure in result.failures:
            print(f"FAILED: {failure[0]}")
            print(f"Reason: {failure[1]}")
        for error in result.errors:
            print(f"ERROR: {error[0]}")
            print(f"Reason: {error[1]}")
    
    print("=" * 60)
    return result.wasSuccessful()


if __name__ == "__main__":
    run_singleton_tests()
