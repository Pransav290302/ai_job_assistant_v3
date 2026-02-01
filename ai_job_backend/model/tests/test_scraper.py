"""
Unit tests for job scraper
"""

import unittest
from model.job_scraper import JobScraper, scrape_job_description


class TestJobScraper(unittest.TestCase):
    """Test cases for JobScraper"""
    
    def test_detect_site(self):
        """Test site detection"""
        scraper = JobScraper()
        
        self.assertEqual(scraper._detect_site("https://linkedin.com/jobs/123"), "linkedin")
        self.assertEqual(scraper._detect_site("https://indeed.com/viewjob?jk=123"), "indeed")
        self.assertEqual(scraper._detect_site("https://boards.greenhouse.io/company/jobs/123"), "greenhouse")
        self.assertEqual(scraper._detect_site("https://glassdoor.com/job-listing/123"), "glassdoor")
        self.assertEqual(scraper._detect_site("https://unknown-site.com/job"), "generic")
    
    def test_clean_text(self):
        """Test text cleaning"""
        scraper = JobScraper()
        
        dirty_text = "  This   is    a   test  \n\n  with   extra   spaces  "
        clean = scraper._clean_text(dirty_text)
        self.assertEqual(clean, "This is a test with extra spaces")
        
        empty = scraper._clean_text("")
        self.assertEqual(empty, "")
    
    def test_scraper_initialization(self):
        """Test scraper initialization"""
        scraper = JobScraper(use_selenium=False)
        self.assertFalse(scraper.use_selenium)
        self.assertIsNotNone(scraper.session)
        scraper.close()
    
    def test_context_manager(self):
        """Test context manager usage"""
        with JobScraper() as scraper:
            self.assertIsNotNone(scraper)
        # Should be cleaned up after context exit


if __name__ == '__main__':
    unittest.main()
