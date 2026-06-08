"""
Conditional Logic Extractor Service - Extracts IF-THEN-UNLESS conditional structures.

This module extracts conditional logic including conditions, consequences, and exceptions
from legal text.
"""

import re
import time
from typing import List, Optional, Tuple
from .models import (
    Condition, Consequence, Exception, ConditionalRule,
    CircularCondition, ImpossibleCondition,
    ConditionalContent, ConditionalExtractionResult
)


class ConditionalLogicExtractor:
    """
    Extracts conditional logic from legal text.
    """
    
    # Condition patterns (IF, WHEN)
    CONDITION_PATTERNS = [
        r'ako\s+([^,.;!?]+?)[,.]',
        r'ukoliko\s+([^,.;!?]+?)[,.]',
        r'kada\s+([^,.;!?]+?)[,.]',
        r'u slučaju\s+([^,.;!?]+?)[,.]',
        r'u slučaju da\s+([^,.;!?]+?)[,.]',
        r'pod uslovom da\s+([^,.;!?]+?)[,.]',
    ]
    
    # Consequence patterns (THEN, MUST, SHALL)
    CONSEQUENCE_PATTERNS = [
        r'tada\s+([^,.;!?]+?[,.;!?])',
        r'onda\s+([^,.;!?]+?[,.;!?])',
        r'mora\s+([^,.;!?]+?[,.;!?])',
        r'dužan je\s+([^,.;!?]+?[,.;!?])',
        r'obavezan je\s+([^,.;!?]+?[,.;!?])',
        r'može\s+([^,.;!?]+?[,.;!?])',
        r'ima pravo\s+([^,.;!?]+?[,.;!?])',
    ]
    
    # Exception patterns (UNLESS, EXCEPT)
    EXCEPTION_PATTERNS = [
        r'osim\s+([^,.;!?]+?[,.;!?])',
        r'izuzev\s+([^,.;!?]+?[,.;!?])',
        r'sem\s+([^,.;!?]+?[,.;!?])',
        r'osim ako\s+([^,.;!?]+?[,.;!?])',
        r'izuzev ako\s+([^,.;!?]+?[,.;!?])',
        r'sem ako\s+([^,.;!?]+?[,.;!?])',
        r'osim u slučaju\s+([^,.;!?]+?[,.;!?])',
    ]
    
    # Complex conditional patterns (IF...THEN)
    COMPLEX_PATTERNS = [
        r'ako\s+([^,.;!?]+?)[,\s]+(?:tada|onda|mora|dužan je|obavezan je)\s+([^,.;!?]+?[,.;!?])',
        r'ukoliko\s+([^,.;!?]+?)[,\s]+(?:tada|onda|mora|dužan je|obavezan je)\s+([^,.;!?]+?[,.;!?])',
        r'u slučaju da\s+([^,.;!?]+?)[,\s]+(?:tada|onda|mora|dužan je|obavezan je)\s+([^,.;!?]+?[,.;!?])',
    ]
    
    # Nested conditional patterns
    NESTED_PATTERNS = [
        r'ako\s+([^,.;!?]+?)[,\s]+a\s+ako\s+([^,.;!?]+?)[,\s]+([^,.;!?]+?[,.;!?])',
    ]
    
    def __init__(self):
        """Initialize the extractor."""
        # Compile patterns for better performance
        self.condition_patterns = [re.compile(p, re.IGNORECASE) for p in self.CONDITION_PATTERNS]
        self.consequence_patterns = [re.compile(p, re.IGNORECASE) for p in self.CONSEQUENCE_PATTERNS]
        self.exception_patterns = [re.compile(p, re.IGNORECASE) for p in self.EXCEPTION_PATTERNS]
        self.complex_patterns = [re.compile(p, re.IGNORECASE) for p in self.COMPLEX_PATTERNS]
        self.nested_patterns = [re.compile(p, re.IGNORECASE) for p in self.NESTED_PATTERNS]
    
    def extract_conditions(self, text: str) -> List[Condition]:
        """
        Extract conditions (IF, WHEN).
        
        Args:
            text: Input text
            
        Returns:
            List of Condition objects
        """
        conditions = []
        lines = text.split('\n')
        
        for pattern in self.condition_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    condition_text = match.group(1).strip()
                    context = match.group(0).strip()
                    
                    # Determine condition type
                    cond_type = "if"
                    if "kada" in context.lower():
                        cond_type = "when"
                    elif "pod uslovom" in context.lower():
                        cond_type = "provided_that"
                    
                    conditions.append(Condition(
                        condition_text=condition_text,
                        condition_type=cond_type,
                        context=context,
                        line_number=line_num
                    ))
        
        return conditions
    
    def extract_consequences(self, text: str) -> List[Consequence]:
        """
        Extract consequences (THEN, MUST, SHALL).
        
        Args:
            text: Input text
            
        Returns:
            List of Consequence objects
        """
        consequences = []
        lines = text.split('\n')
        
        for pattern in self.consequence_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    consequence_text = match.group(1).strip()
                    context = match.group(0).strip()
                    
                    # Determine consequence type
                    cons_type = "then"
                    if "mora" in context.lower() or "dužan" in context.lower() or "obavezan" in context.lower():
                        cons_type = "must"
                    elif "može" in context.lower() or "ima pravo" in context.lower():
                        cons_type = "may"
                    
                    consequences.append(Consequence(
                        consequence_text=consequence_text,
                        consequence_type=cons_type,
                        context=context,
                        line_number=line_num
                    ))
        
        return consequences
    
    def extract_exceptions(self, text: str) -> List[Exception]:
        """
        Extract exceptions (UNLESS, EXCEPT).
        
        Args:
            text: Input text
            
        Returns:
            List of Exception objects
        """
        exceptions = []
        lines = text.split('\n')
        
        for pattern in self.exception_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    exception_text = match.group(1).strip()
                    context = match.group(0).strip()
                    
                    # Determine exception type
                    exc_type = "unless"
                    if "izuzev" in context.lower():
                        exc_type = "except"
                    elif "sem" in context.lower():
                        exc_type = "excluding"
                    
                    exceptions.append(Exception(
                        exception_text=exception_text,
                        exception_type=exc_type,
                        context=context,
                        line_number=line_num
                    ))
        
        return exceptions
    
    def extract_rules(self, text: str) -> List[ConditionalRule]:
        """
        Extract complete conditional rules (IF-THEN-UNLESS).
        
        Args:
            text: Input text
            
        Returns:
            List of ConditionalRule objects
        """
        rules = []
        lines = text.split('\n')
        
        # Extract complex rules (IF...THEN)
        for pattern in self.complex_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    condition_text = match.group(1).strip()
                    consequence_text = match.group(2).strip()
                    rule_text = match.group(0).strip()
                    
                    condition = Condition(
                        condition_text=condition_text,
                        condition_type="if",
                        context=condition_text,
                        line_number=line_num
                    )
                    
                    consequence = Consequence(
                        consequence_text=consequence_text,
                        consequence_type="must",
                        context=consequence_text,
                        line_number=line_num
                    )
                    
                    rules.append(ConditionalRule(
                        conditions=[condition],
                        consequences=[consequence],
                        exceptions=[],
                        rule_text=rule_text,
                        rule_type="simple",
                        line_number=line_num
                    ))
        
        # Extract nested rules
        for pattern in self.nested_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    condition1_text = match.group(1).strip()
                    condition2_text = match.group(2).strip()
                    consequence_text = match.group(3).strip()
                    rule_text = match.group(0).strip()
                    
                    condition1 = Condition(
                        condition_text=condition1_text,
                        condition_type="if",
                        context=condition1_text,
                        line_number=line_num
                    )
                    
                    condition2 = Condition(
                        condition_text=condition2_text,
                        condition_type="if",
                        context=condition2_text,
                        line_number=line_num
                    )
                    
                    consequence = Consequence(
                        consequence_text=consequence_text,
                        consequence_type="then",
                        context=consequence_text,
                        line_number=line_num
                    )
                    
                    rules.append(ConditionalRule(
                        conditions=[condition1, condition2],
                        consequences=[consequence],
                        exceptions=[],
                        rule_text=rule_text,
                        rule_type="nested",
                        line_number=line_num
                    ))
        
        return rules
    
    def detect_circular_conditions(self, conditions: List[Condition], rules: List[ConditionalRule]) -> List[CircularCondition]:
        """
        Detect circular conditions (A depends on B, B depends on A).
        
        Args:
            conditions: List of extracted conditions
            rules: List of extracted rules
            
        Returns:
            List of CircularCondition objects
        """
        circular = []
        
        # Build dependency map from rules
        dependencies = {}  # condition -> list of conditions it depends on
        
        for rule in rules:
            for cond in rule.conditions:
                cond_text = cond.condition_text.lower()
                if cond_text not in dependencies:
                    dependencies[cond_text] = []
                
                # Check if consequence references other conditions
                for cons in rule.consequences:
                    cons_text = cons.consequence_text.lower()
                    # Look for condition keywords in consequence
                    for other_cond in conditions:
                        other_text = other_cond.condition_text.lower()
                        if other_text != cond_text and other_text in cons_text:
                            dependencies[cond_text].append(other_text)
        
        # Detect circular dependencies
        checked = set()
        for cond1, deps in dependencies.items():
            if cond1 in checked:
                continue
            
            for cond2 in deps:
                if cond2 in dependencies:
                    # Check if cond2 depends on cond1 (direct circular)
                    if cond1 in dependencies[cond2]:
                        circular.append(CircularCondition(
                            condition1=cond1,
                            condition2=cond2,
                            chain=[cond1, cond2, cond1],
                            context=f"{cond1} -> {cond2} -> {cond1}",
                            confidence=0.8
                        ))
                        checked.add(cond1)
                        checked.add(cond2)
                    
                    # Check for indirect circular (A -> B -> C -> A)
                    else:
                        for cond3 in dependencies.get(cond2, []):
                            if cond3 in dependencies and cond1 in dependencies[cond3]:
                                circular.append(CircularCondition(
                                    condition1=cond1,
                                    condition2=cond3,
                                    chain=[cond1, cond2, cond3, cond1],
                                    context=f"{cond1} -> {cond2} -> {cond3} -> {cond1}",
                                    confidence=0.7
                                ))
                                checked.add(cond1)
                                checked.add(cond2)
                                checked.add(cond3)
        
        return circular
    
    def detect_impossible_conditions(self, text: str, conditions: List[Condition], rules: List[ConditionalRule]) -> List[ImpossibleCondition]:
        """
        Detect impossible or contradictory conditions.
        
        Args:
            text: Input text
            conditions: List of extracted conditions
            rules: List of extracted rules
            
        Returns:
            List of ImpossibleCondition objects
        """
        impossible = []
        
        # Patterns for logical contradictions
        CONTRADICTION_PATTERNS = [
            (r'(istovremeno|u isto vreme).*(i|ali).*(ne može|zabranjeno)', 'mutual_exclusion'),
            (r'(mora|dužan).*(i|ali).*(ne sme|zabranjeno)', 'logical'),
            (r'(pre nego što).*(nakon što)', 'temporal'),
            (r'(ako je).*(i ako nije)', 'logical'),
        ]
        
        # Check for contradictions in text
        for pattern, contradiction_type in CONTRADICTION_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = match.group(0)
                impossible.append(ImpossibleCondition(
                    condition_text=context,
                    contradiction_type=contradiction_type,
                    reason=f"Detected {contradiction_type} contradiction",
                    context=context,
                    confidence=0.75
                ))
        
        # Check for mutually exclusive conditions in rules
        for i, rule1 in enumerate(rules):
            for rule2 in rules[i+1:]:
                # Check if conditions are contradictory
                for cond1 in rule1.conditions:
                    for cond2 in rule2.conditions:
                        cond1_text = cond1.condition_text.lower()
                        cond2_text = cond2.condition_text.lower()
                        
                        # Look for negation patterns
                        if "ne" in cond2_text and cond1_text.replace("ne ", "") in cond2_text:
                            impossible.append(ImpossibleCondition(
                                condition_text=f"{cond1_text} AND {cond2_text}",
                                contradiction_type="logical",
                                reason="Mutually exclusive conditions",
                                context=f"Rule 1: {rule1.rule_text} | Rule 2: {rule2.rule_text}",
                                confidence=0.8
                            ))
        
        # Check for temporal impossibilities
        TEMPORAL_KEYWORDS = {
            'pre': 'before',
            'nakon': 'after',
            'istovremeno': 'simultaneously',
            'u isto vreme': 'at the same time'
        }
        
        for rule in rules:
            rule_text = rule.rule_text.lower()
            temporal_found = []
            
            for keyword in TEMPORAL_KEYWORDS:
                if keyword in rule_text:
                    temporal_found.append(keyword)
            
            # If both "pre" and "nakon" reference the same event
            if 'pre' in temporal_found and 'nakon' in temporal_found:
                impossible.append(ImpossibleCondition(
                    condition_text=rule.rule_text,
                    contradiction_type="temporal",
                    reason="Cannot be both before and after the same event",
                    context=rule.rule_text,
                    confidence=0.7
                ))
        
        return impossible
    
    def extract(self, text: str) -> ConditionalExtractionResult:
        """
        Extract all conditional logic.
        
        Args:
            text: Input text
            
        Returns:
            ConditionalExtractionResult
        """
        start_time = time.time()
        
        # Extract all types
        conditions = self.extract_conditions(text)
        consequences = self.extract_consequences(text)
        exceptions = self.extract_exceptions(text)
        rules = self.extract_rules(text)
        circular_conditions = self.detect_circular_conditions(conditions, rules)
        impossible_conditions = self.detect_impossible_conditions(text, conditions, rules)
        
        content = ConditionalContent(
            conditions=conditions,
            consequences=consequences,
            exceptions=exceptions,
            rules=rules,
            circular_conditions=circular_conditions,
            impossible_conditions=impossible_conditions
        )
        
        processing_time = time.time() - start_time
        
        return ConditionalExtractionResult(
            content=content,
            processing_time=processing_time
        )


# Singleton instance
_extractor = None

def get_extractor() -> ConditionalLogicExtractor:
    """Get singleton extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = ConditionalLogicExtractor()
    return _extractor


def extract_conditional_logic(text: str) -> dict:
    """
    Extract conditional logic from text.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with extraction result
    """
    extractor = get_extractor()
    result = extractor.extract(text)
    return result.to_dict()

# Made with Bob
