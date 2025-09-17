#!/usr/bin/env python3
"""
Unit tests for Holiday Image Generator
Tests data preservation, appending, and caption regeneration functionality
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add parent directory to path to import holiday_image_generator
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts', 'image_generation'))
from holiday_image_generator import HolidayImageGenerator

class TestHolidayImageGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_holidays_file = os.path.join(self.test_dir, 'test_holidays.json')
        self.test_output_file = os.path.join(self.test_dir, 'test_output.json')
        
        # Sample holiday data
        self.sample_holidays = [
            {
                "holiday_id": 1,
                "name": "Test Holiday 1",
                "date": "2025-12-01",
                "description": "Test holiday 1",
                "occasion_id": 1,
                "country": "US",
                "type": "Test Holiday",
                "created_at": "2025-01-01 00:00:00",
                "updated_at": None
            },
            {
                "holiday_id": 2,
                "name": "Test Holiday 2",
                "date": "2025-12-02",
                "description": "Test holiday 2",
                "occasion_id": 2,
                "country": "US",
                "type": "Test Holiday",
                "created_at": "2025-01-01 00:00:00",
                "updated_at": None
            },
            {
                "holiday_id": 3,
                "name": "Test Holiday 3",
                "date": "2025-12-03",
                "description": "Test holiday 3",
                "occasion_id": 3,
                "country": "US",
                "type": "Test Holiday",
                "created_at": "2025-01-01 00:00:00",
                "updated_at": None
            }
        ]
        
        # Write sample holidays to file
        with open(self.test_holidays_file, 'w') as f:
            json.dump(self.sample_holidays, f)
        
        # Create generator instance
        self.generator = HolidayImageGenerator()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_data_preservation_on_incremental_save(self):
        """Test that existing data is preserved when saving incrementally"""
        # Create initial output with some data
        initial_data = {
            "generated_at": "2025-12-01T10:00:00",
            "total_dates": 1,
            "holidays_by_date": {
                "2025-12-01": {
                    "date": "2025-12-01",
                    "selected_holiday": "Test Holiday 1",
                    "caption": "Initial caption",
                    "content_ready": True,
                    "generated_at": "2025-12-01T10:00:00"
                }
            }
        }
        
        with open(self.test_output_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        # Add new data
        new_data = {
            "2025-12-02": {
                "date": "2025-12-02",
                "selected_holiday": "Test Holiday 2",
                "caption": "New caption",
                "content_ready": True,
                "generated_at": "2025-12-01T11:00:00"
            }
        }
        
        # Use the fixed save method
        self.generator.save_complete_output_fixed(new_data, self.test_output_file)
        
        # Verify both old and new data exist
        with open(self.test_output_file, 'r') as f:
            result = json.load(f)
        
        self.assertIn("2025-12-01", result["holidays_by_date"])
        self.assertIn("2025-12-02", result["holidays_by_date"])
        self.assertEqual(result["total_dates"], 2)
        self.assertEqual(result["holidays_by_date"]["2025-12-01"]["caption"], "Initial caption")
        self.assertEqual(result["holidays_by_date"]["2025-12-02"]["caption"], "New caption")
    
    def test_data_overwrite_prevention(self):
        """Test that existing complete entries are not overwritten unless explicitly requested"""
        # Create initial complete data
        initial_data = {
            "generated_at": "2025-12-01T10:00:00",
            "total_dates": 1,
            "holidays_by_date": {
                "2025-12-01": {
                    "date": "2025-12-01",
                    "selected_holiday": "Test Holiday 1",
                    "caption": "Original caption",
                    "content_ready": True,
                    "generated_at": "2025-12-01T10:00:00"
                }
            }
        }
        
        with open(self.test_output_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        # Try to overwrite with new data
        overwrite_data = {
            "2025-12-01": {
                "date": "2025-12-01",
                "selected_holiday": "Test Holiday 1",
                "caption": "Modified caption",
                "content_ready": True,
                "generated_at": "2025-12-01T12:00:00"
            }
        }
        
        # This should NOT overwrite existing data when preserve_existing=True
        # But the current implementation replaces data for the same date
        # Let me fix the method to truly preserve existing data
        self.generator.save_complete_output_fixed(overwrite_data, self.test_output_file, preserve_existing=True, skip_existing_dates=True)
        
        with open(self.test_output_file, 'r') as f:
            result = json.load(f)
        
        # Original data should be preserved
        self.assertEqual(result["holidays_by_date"]["2025-12-01"]["caption"], "Original caption")
        self.assertEqual(result["holidays_by_date"]["2025-12-01"]["generated_at"], "2025-12-01T10:00:00")
    
    def test_caption_only_regeneration(self):
        """Test regenerating captions for existing images"""
        # Create data with existing images but missing captions
        existing_data = {
            "generated_at": "2025-12-01T10:00:00",
            "total_dates": 1,
            "holidays_by_date": {
                "2025-12-01": {
                    "date": "2025-12-01",
                    "original_holidays": [self.sample_holidays[0]],  # Add original holidays
                    "selected_holiday": "Test Holiday 1",
                    "caption": "",  # Missing caption
                    "background_image_path": "assets/images/holiday_2025_12_01_background.png",
                    "final_image_path": "assets/images/holiday_2025_12_01_background_with_text.png",
                    "content_ready": False,  # Not ready due to missing caption
                    "generated_at": "2025-12-01T10:00:00"
                }
            }
        }
        
        with open(self.test_output_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        # Mock AI generation for caption only
        mock_ai_result = {
            "selected_holiday": "Test Holiday 1",
            "tone_category": "Festive",
            "caption": "New generated caption",
            "image_prompt": "Test prompt"
        }
        
        with patch.object(self.generator, 'generate_image_prompt_and_caption', return_value=mock_ai_result):
            with patch.object(self.generator, 'generate_image_with_dalle', return_value=None):  # Skip image generation
                # Process caption regeneration
                result = self.generator.regenerate_captions_only(self.test_output_file, ["2025-12-01"])
        
        # Verify caption was updated but images preserved
        with open(self.test_output_file, 'r') as f:
            updated_data = json.load(f)
        
        holiday_data = updated_data["holidays_by_date"]["2025-12-01"]
        self.assertEqual(holiday_data["caption"], "New generated caption")
        self.assertEqual(holiday_data["background_image_path"], "assets/images/holiday_2025_12_01_background.png")
        self.assertEqual(holiday_data["final_image_path"], "assets/images/holiday_2025_12_01_background_with_text.png")
        self.assertTrue(holiday_data["content_ready"])
    
    def test_batch_processing_data_integrity(self):
        """Test that batch processing maintains data integrity"""
        # Mock AI and image generation
        mock_ai_result = {
            "selected_holiday": "Mock Holiday",
            "tone_category": "Festive",
            "caption": "Mock caption",
            "image_prompt": "Mock prompt"
        }
        
        with patch.object(self.generator, 'generate_image_prompt_and_caption', return_value=mock_ai_result):
            with patch.object(self.generator, 'generate_image_with_dalle', return_value="mock_image_path.png"):
                with patch.object(self.generator, 'apply_text_overlays', return_value="mock_final_path.png"):
                    # Process holidays
                    result = self.generator.process_holidays(
                        holidays_file=self.test_holidays_file,
                        output_file=self.test_output_file,
                        skip_existing=True
                    )
        
        # Verify all holidays were processed
        self.assertEqual(len(result), 3)
        
        # Verify data structure
        with open(self.test_output_file, 'r') as f:
            output_data = json.load(f)
        
        self.assertEqual(output_data["total_dates"], 3)
        self.assertIn("2025-12-01", output_data["holidays_by_date"])
        self.assertIn("2025-12-02", output_data["holidays_by_date"])
        self.assertIn("2025-12-03", output_data["holidays_by_date"])
        
        # Verify each entry has required fields
        for date, holiday_data in output_data["holidays_by_date"].items():
            self.assertIn("date", holiday_data)
            self.assertIn("selected_holiday", holiday_data)
            self.assertIn("caption", holiday_data)
            self.assertIn("content_ready", holiday_data)
            self.assertIn("generated_at", holiday_data)
    
    def test_skip_existing_functionality(self):
        """Test that skip_existing parameter works correctly"""
        # Create initial data
        initial_data = {
            "generated_at": "2025-12-01T10:00:00",
            "total_dates": 1,
            "holidays_by_date": {
                "2025-12-01": {
                    "date": "2025-12-01",
                    "selected_holiday": "Test Holiday 1",
                    "caption": "Original caption",
                    "content_ready": True,
                    "generated_at": "2025-12-01T10:00:00"
                }
            }
        }
        
        with open(self.test_output_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        # Mock AI generation (should not be called for existing content)
        mock_ai_result = {
            "selected_holiday": "Mock Holiday",
            "tone_category": "Festive",
            "caption": "Mock caption",
            "image_prompt": "Mock prompt"
        }
        
        with patch.object(self.generator, 'generate_image_prompt_and_caption', return_value=mock_ai_result) as mock_ai:
            with patch.object(self.generator, 'generate_image_with_dalle', return_value="mock_image_path.png") as mock_dalle:
                with patch.object(self.generator, 'apply_text_overlays', return_value="mock_final_path.png"):
                    # Process with skip_existing=True
                    result = self.generator.process_holidays(
                        holidays_file=self.test_holidays_file,
                        output_file=self.test_output_file,
                        skip_existing=True
                    )
        
        # AI should be called only for new dates (2025-12-02, 2025-12-03)
        self.assertEqual(mock_ai.call_count, 2)
        
        # Verify original data is preserved
        with open(self.test_output_file, 'r') as f:
            output_data = json.load(f)
        
        self.assertEqual(output_data["holidays_by_date"]["2025-12-01"]["caption"], "Original caption")
    
    def run_live_test_next_5_dates(self):
        """Live test for next 5 dates - not a unit test but a validation function"""
        from datetime import datetime, timedelta
        
        # Get next 5 dates
        today = datetime.now()
        test_dates = []
        for i in range(1, 6):  # Next 5 days
            test_date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
            test_dates.append(test_date)
        
        print(f"Testing caption regeneration for dates: {test_dates}")
        
        # Check if these dates exist in current output
        if os.path.exists('data/output/upcoming_holidays_output.json'):
            with open('data/output/upcoming_holidays_output.json', 'r') as f:
                current_data = json.load(f)
            
            existing_dates = [date for date in test_dates 
                            if date in current_data.get('holidays_by_date', {})]
            
            if existing_dates:
                print(f"Found existing data for dates: {existing_dates}")
                
                # Test caption regeneration
                generator = HolidayImageGenerator()
                try:
                    result = generator.regenerate_captions_only('data/output/upcoming_holidays_output.json', existing_dates)
                    print(f"✅ Successfully regenerated captions for {len(result)} dates")
                    return True
                except Exception as e:
                    print(f"❌ Caption regeneration failed: {e}")
                    return False
            else:
                print("No existing data found for test dates")
                return False
        else:
            print("No existing output file found")
            return False

def run_tests():
    """Run all unit tests"""
    unittest.main(verbosity=2, exit=False)

def run_live_validation():
    """Run live validation test"""
    test_instance = TestHolidayImageGenerator()
    test_instance.setUp()
    result = test_instance.run_live_test_next_5_dates()
    test_instance.tearDown()
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "live":
        # Run live validation
        print("Running live validation test...")
        success = run_live_validation()
        sys.exit(0 if success else 1)
    else:
        # Run unit tests
        run_tests()