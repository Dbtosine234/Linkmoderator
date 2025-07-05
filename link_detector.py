"""
Link Detector - Detects and extracts URLs from messages
"""

import re
import logging
from typing import List

class LinkDetector:
    """Detects links in text messages using regular expressions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Comprehensive URL regex pattern
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            r'|(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
            r'(?:[a-zA-Z]{2,}))(?::[0-9]{1,5})?(?:/[^\s]*)?'
            r'|www\.(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
            r'(?:[a-zA-Z]{2,})(?::[0-9]{1,5})?(?:/[^\s]*)?',
            re.IGNORECASE
        )
        
        # Additional patterns for common URL formats
        self.additional_patterns = [
            # Telegram links
            re.compile(r't\.me/[a-zA-Z0-9_]+', re.IGNORECASE),
            # Short URLs
            re.compile(r'bit\.ly/[a-zA-Z0-9]+', re.IGNORECASE),
            re.compile(r'tinyurl\.com/[a-zA-Z0-9]+', re.IGNORECASE),
            # Common domains without protocol
            re.compile(r'(?:^|\s)([a-zA-Z0-9-]+\.(?:com|org|net|edu|gov|co|io|me|tv|xyz|info|biz)(?:/[^\s]*)?)', re.IGNORECASE)
        ]
    
    def extract_links(self, text: str) -> List[str]:
        """
        Extract all links from the given text
        
        Args:
            text (str): The text to search for links
            
        Returns:
            List[str]: List of found URLs
        """
        if not text:
            return []
        
        links = []
        
        # Find URLs with main pattern
        main_matches = self.url_pattern.findall(text)
        links.extend(main_matches)
        
        # Find URLs with additional patterns
        for pattern in self.additional_patterns:
            additional_matches = pattern.findall(text)
            links.extend(additional_matches)
        
        # Remove duplicates and clean up
        unique_links = []
        seen = set()
        
        for link in links:
            # Clean up the link
            cleaned_link = link.strip()
            if cleaned_link and cleaned_link.lower() not in seen:
                seen.add(cleaned_link.lower())
                unique_links.append(cleaned_link)
        
        if unique_links:
            self.logger.debug(f"Found {len(unique_links)} links in message: {unique_links}")
        
        return unique_links
    
    def contains_links(self, text: str) -> bool:
        """
        Check if text contains any links
        
        Args:
            text (str): The text to check
            
        Returns:
            bool: True if links are found, False otherwise
        """
        return len(self.extract_links(text)) > 0
    
    def is_suspicious_link(self, url: str) -> bool:
        """
        Check if a URL might be suspicious (basic checks)
        
        Args:
            url (str): The URL to check
            
        Returns:
            bool: True if URL seems suspicious
        """
        suspicious_indicators = [
            # URL shorteners (higher risk)
            'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 't.co',
            # Common phishing domains patterns
            '.tk', '.ml', '.ga', '.cf',
            # Suspicious patterns
            'bit.do', 'cutt.ly', 'short.link'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in suspicious_indicators)
