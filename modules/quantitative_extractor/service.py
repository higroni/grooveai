"""
Quantitative Extractor Service - Extracts quantitative standards, thresholds, and limits.

This module extracts numeric standards (minimum/maximum), thresholds, percentages,
and monetary amounts from legal text.
"""

import re
import time
from typing import List, Optional, Tuple
from .models import (
    QuantitativeStandard, Threshold, Percentage, MonetaryAmount,
    QuantitativeContent, QuantitativeExtractionResult
)


class QuantitativeExtractor:
    """
    Extracts quantitative content from legal text.
    """
    
    # Standard patterns (minimum/maximum)
    MINIMUM_PATTERNS = [
        r'najmanje\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'minimum\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'ne\s+manje\s+od\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'minimalno\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
    ]
    
    MAXIMUM_PATTERNS = [
        r'najviše\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'maksimum\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'ne\s+više\s+od\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'maksimalno\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
    ]
    
    EXACT_PATTERNS = [
        r'tačno\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'iznosi\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
    ]
    
    RANGE_PATTERNS = [
        r'od\s+(\d+(?:[.,]\d+)?)\s+do\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'između\s+(\d+(?:[.,]\d+)?)\s+i\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
    ]
    
    # Threshold patterns
    THRESHOLD_PATTERNS = [
        r'prag\s+od\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'granica\s+od\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'limit\s+od\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
    ]
    
    UPPER_LIMIT_PATTERNS = [
        r'gornja\s+granica\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'ne\s+prelazi\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
    ]
    
    LOWER_LIMIT_PATTERNS = [
        r'donja\s+granica\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
        r'ne\s+ispod\s+(\d+(?:[.,]\d+)?)\s*([a-zšđčćž]+)?[^,.;!?]+?[,.;!?]',
    ]
    
    # Percentage patterns
    PERCENTAGE_PATTERNS = [
        r'(\d+(?:[.,]\d+)?)\s*%[^,.;!?]+?[,.;!?]',
        r'(\d+(?:[.,]\d+)?)\s*procent[a]?[^,.;!?]+?[,.;!?]',
        r'(\d+(?:[.,]\d+)?)\s*posto[^,.;!?]+?[,.;!?]',
    ]
    
    # Monetary amount patterns
    MONETARY_PATTERNS = [
        r'(\d+(?:[.,]\d+)?)\s*dinara[^,.;!?]+?[,.;!?]',
        r'(\d+(?:[.,]\d+)?)\s*RSD[^,.;!?]+?[,.;!?]',
        r'(\d+(?:[.,]\d+)?)\s*evra[^,.;!?]+?[,.;!?]',
        r'(\d+(?:[.,]\d+)?)\s*EUR[^,.;!?]+?[,.;!?]',
    ]
    
    def __init__(self):
        """Initialize the extractor."""
        # Compile patterns for better performance
        self.minimum_patterns = [re.compile(p, re.IGNORECASE) for p in self.MINIMUM_PATTERNS]
        self.maximum_patterns = [re.compile(p, re.IGNORECASE) for p in self.MAXIMUM_PATTERNS]
        self.exact_patterns = [re.compile(p, re.IGNORECASE) for p in self.EXACT_PATTERNS]
        self.range_patterns = [re.compile(p, re.IGNORECASE) for p in self.RANGE_PATTERNS]
        
        self.threshold_patterns = [re.compile(p, re.IGNORECASE) for p in self.THRESHOLD_PATTERNS]
        self.upper_limit_patterns = [re.compile(p, re.IGNORECASE) for p in self.UPPER_LIMIT_PATTERNS]
        self.lower_limit_patterns = [re.compile(p, re.IGNORECASE) for p in self.LOWER_LIMIT_PATTERNS]
        
        self.percentage_patterns = [re.compile(p, re.IGNORECASE) for p in self.PERCENTAGE_PATTERNS]
        self.monetary_patterns = [re.compile(p, re.IGNORECASE) for p in self.MONETARY_PATTERNS]
    
    def extract_standards(self, text: str) -> List[QuantitativeStandard]:
        """
        Extract quantitative standards (minimum/maximum/exact/range).
        
        Args:
            text: Input text
            
        Returns:
            List of QuantitativeStandard objects
        """
        standards = []
        lines = text.split('\n')
        
        # Extract minimums
        for pattern in self.minimum_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    value = match.group(1)
                    unit = match.group(2) if len(match.groups()) > 1 else None
                    context = match.group(0).strip()
                    
                    standards.append(QuantitativeStandard(
                        type="minimum",
                        value=value,
                        unit=unit,
                        context=context,
                        applies_to=None,
                        line_number=line_num
                    ))
        
        # Extract maximums
        for pattern in self.maximum_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    value = match.group(1)
                    unit = match.group(2) if len(match.groups()) > 1 else None
                    context = match.group(0).strip()
                    
                    standards.append(QuantitativeStandard(
                        type="maximum",
                        value=value,
                        unit=unit,
                        context=context,
                        applies_to=None,
                        line_number=line_num
                    ))
        
        # Extract exact values
        for pattern in self.exact_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    value = match.group(1)
                    unit = match.group(2) if len(match.groups()) > 1 else None
                    context = match.group(0).strip()
                    
                    standards.append(QuantitativeStandard(
                        type="exact",
                        value=value,
                        unit=unit,
                        context=context,
                        applies_to=None,
                        line_number=line_num
                    ))
        
        # Extract ranges
        for pattern in self.range_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    value1 = match.group(1)
                    value2 = match.group(2)
                    unit = match.group(3) if len(match.groups()) > 2 else None
                    context = match.group(0).strip()
                    
                    standards.append(QuantitativeStandard(
                        type="range",
                        value=f"{value1}-{value2}",
                        unit=unit,
                        context=context,
                        applies_to=None,
                        line_number=line_num
                    ))
        
        return standards
    
    def extract_thresholds(self, text: str) -> List[Threshold]:
        """
        Extract thresholds and limits.
        
        Args:
            text: Input text
            
        Returns:
            List of Threshold objects
        """
        thresholds = []
        lines = text.split('\n')
        
        # Extract general thresholds
        for pattern in self.threshold_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    value = match.group(1)
                    unit = match.group(2) if len(match.groups()) > 1 else None
                    context = match.group(0).strip()
                    
                    thresholds.append(Threshold(
                        type="threshold",
                        value=value,
                        unit=unit,
                        context=context,
                        consequence=None,
                        line_number=line_num
                    ))
        
        # Extract upper limits
        for pattern in self.upper_limit_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    value = match.group(1)
                    unit = match.group(2) if len(match.groups()) > 1 else None
                    context = match.group(0).strip()
                    
                    thresholds.append(Threshold(
                        type="upper_limit",
                        value=value,
                        unit=unit,
                        context=context,
                        consequence=None,
                        line_number=line_num
                    ))
        
        # Extract lower limits
        for pattern in self.lower_limit_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    value = match.group(1)
                    unit = match.group(2) if len(match.groups()) > 1 else None
                    context = match.group(0).strip()
                    
                    thresholds.append(Threshold(
                        type="lower_limit",
                        value=value,
                        unit=unit,
                        context=context,
                        consequence=None,
                        line_number=line_num
                    ))
        
        return thresholds
    
    def extract_percentages(self, text: str) -> List[Percentage]:
        """
        Extract percentage values.
        
        Args:
            text: Input text
            
        Returns:
            List of Percentage objects
        """
        percentages = []
        lines = text.split('\n')
        
        for pattern in self.percentage_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    value = match.group(1)
                    context = match.group(0).strip()
                    
                    percentages.append(Percentage(
                        value=value,
                        context=context,
                        applies_to=None,
                        line_number=line_num
                    ))
        
        return percentages
    
    def extract_monetary_amounts(self, text: str) -> List[MonetaryAmount]:
        """
        Extract monetary amounts.
        
        Args:
            text: Input text
            
        Returns:
            List of MonetaryAmount objects
        """
        amounts = []
        lines = text.split('\n')
        
        for pattern in self.monetary_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    amount = match.group(1)
                    context = match.group(0).strip()
                    
                    # Determine currency
                    currency = "RSD"
                    if "evra" in context.lower() or "EUR" in context:
                        currency = "EUR"
                    
                    amounts.append(MonetaryAmount(
                        amount=amount,
                        currency=currency,
                        context=context,
                        purpose=None,
                        line_number=line_num
                    ))
        
        return amounts
    
    def extract(self, text: str) -> QuantitativeExtractionResult:
        """
        Extract all quantitative content.
        
        Args:
            text: Input text
            
        Returns:
            QuantitativeExtractionResult
        """
        start_time = time.time()
        
        # Extract all types
        standards = self.extract_standards(text)
        thresholds = self.extract_thresholds(text)
        percentages = self.extract_percentages(text)
        monetary_amounts = self.extract_monetary_amounts(text)
        
        content = QuantitativeContent(
            standards=standards,
            thresholds=thresholds,
            percentages=percentages,
            monetary_amounts=monetary_amounts
        )
        
        processing_time = time.time() - start_time
        
        return QuantitativeExtractionResult(
            content=content,
            processing_time=processing_time
        )


# Singleton instance
_extractor = None

def get_extractor() -> QuantitativeExtractor:
    """Get singleton extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = QuantitativeExtractor()
    return _extractor


def extract_quantitative(text: str) -> dict:
    """
    Extract quantitative content from text.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with extraction result
    """
    extractor = get_extractor()
    result = extractor.extract(text)
    return result.to_dict()

# Made with Bob
