"""
Data models for Conditional Logic Extractor module.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class Condition(BaseModel):
    """Represents a condition in conditional logic."""
    
    condition_text: str = Field(..., description="The condition text")
    condition_type: str = Field(..., description="Type: 'if', 'when', 'unless', 'provided_that'")
    context: str = Field(..., description="Full context of the condition")
    line_number: Optional[int] = Field(None, description="Line number in source")


class Consequence(BaseModel):
    """Represents a consequence/result in conditional logic."""
    
    consequence_text: str = Field(..., description="The consequence text")
    consequence_type: str = Field(..., description="Type: 'then', 'must', 'shall', 'may'")
    context: str = Field(..., description="Full context of the consequence")
    line_number: Optional[int] = Field(None, description="Line number in source")


class Exception(BaseModel):
    """Represents an exception in conditional logic."""
    
    exception_text: str = Field(..., description="The exception text")
    exception_type: str = Field(..., description="Type: 'unless', 'except', 'excluding'")
    context: str = Field(..., description="Full context of the exception")
    line_number: Optional[int] = Field(None, description="Line number in source")


class ConditionalRule(BaseModel):
    """Represents a complete conditional rule (IF-THEN-UNLESS)."""
    
    conditions: List[Condition] = Field(default_factory=list)
    consequences: List[Consequence] = Field(default_factory=list)
    exceptions: List[Exception] = Field(default_factory=list)
    rule_text: str = Field(..., description="Complete rule text")
    rule_type: str = Field(..., description="Type: 'simple', 'complex', 'nested'")
    line_number: Optional[int] = Field(None, description="Line number in source")


class CircularCondition(BaseModel):
    """Represents a circular condition (A depends on B, B depends on A)."""
    
    condition1: str = Field(..., description="First condition")
    condition2: str = Field(..., description="Second condition")
    chain: List[str] = Field(default_factory=list, description="Chain of dependencies")
    context: str = Field(..., description="Full context")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class ImpossibleCondition(BaseModel):
    """Represents an impossible or contradictory condition."""
    
    condition_text: str = Field(..., description="The impossible condition")
    contradiction_type: str = Field(..., description="Type: 'logical', 'temporal', 'mutual_exclusion'")
    reason: str = Field(..., description="Why the condition is impossible")
    context: str = Field(..., description="Full context")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class ConditionalContent(BaseModel):
    """Container for all conditional logic content."""
    
    conditions: List[Condition] = Field(default_factory=list)
    consequences: List[Consequence] = Field(default_factory=list)
    exceptions: List[Exception] = Field(default_factory=list)
    rules: List[ConditionalRule] = Field(default_factory=list)
    circular_conditions: List[CircularCondition] = Field(default_factory=list)
    impossible_conditions: List[ImpossibleCondition] = Field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "conditions": [c.model_dump() for c in self.conditions],
            "consequences": [c.model_dump() for c in self.consequences],
            "exceptions": [e.model_dump() for e in self.exceptions],
            "rules": [r.model_dump() for r in self.rules],
            "circular_conditions": [c.model_dump() for c in self.circular_conditions],
            "impossible_conditions": [i.model_dump() for i in self.impossible_conditions]
        }
    
    def count_total(self) -> int:
        """Get total count of all conditional elements."""
        return (len(self.conditions) + len(self.consequences) +
                len(self.exceptions) + len(self.rules) +
                len(self.circular_conditions) + len(self.impossible_conditions))


class ConditionalExtractionResult(BaseModel):
    """Result of conditional logic extraction."""
    
    content: ConditionalContent
    processing_time: float = Field(..., description="Processing time in seconds")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "content": self.content.to_dict(),
            "processing_time": self.processing_time,
            "total_elements": self.content.count_total()
        }

# Made with Bob
