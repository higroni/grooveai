"""
Data models for Quantitative Extractor module.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class QuantitativeStandard(BaseModel):
    """Represents a quantitative standard (minimum/maximum)."""
    
    type: str = Field(..., description="Type: 'minimum', 'maximum', 'exact', 'range'")
    value: str = Field(..., description="Numeric value or range")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    context: str = Field(..., description="Context where standard appears")
    applies_to: Optional[str] = Field(None, description="What the standard applies to")
    line_number: Optional[int] = Field(None, description="Line number in source")


class Threshold(BaseModel):
    """Represents a threshold or limit."""
    
    type: str = Field(..., description="Type: 'upper_limit', 'lower_limit', 'threshold'")
    value: str = Field(..., description="Numeric value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    context: str = Field(..., description="Context where threshold appears")
    consequence: Optional[str] = Field(None, description="What happens when threshold is crossed")
    line_number: Optional[int] = Field(None, description="Line number in source")


class Percentage(BaseModel):
    """Represents a percentage value."""
    
    value: str = Field(..., description="Percentage value")
    context: str = Field(..., description="Context where percentage appears")
    applies_to: Optional[str] = Field(None, description="What the percentage applies to")
    line_number: Optional[int] = Field(None, description="Line number in source")


class MonetaryAmount(BaseModel):
    """Represents a monetary amount."""
    
    amount: str = Field(..., description="Monetary amount")
    currency: str = Field(default="RSD", description="Currency code")
    context: str = Field(..., description="Context where amount appears")
    purpose: Optional[str] = Field(None, description="Purpose of the amount")
    line_number: Optional[int] = Field(None, description="Line number in source")


class QuantitativeContent(BaseModel):
    """Container for all quantitative content."""
    
    standards: List[QuantitativeStandard] = Field(default_factory=list)
    thresholds: List[Threshold] = Field(default_factory=list)
    percentages: List[Percentage] = Field(default_factory=list)
    monetary_amounts: List[MonetaryAmount] = Field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "standards": [s.model_dump() for s in self.standards],
            "thresholds": [t.model_dump() for t in self.thresholds],
            "percentages": [p.model_dump() for p in self.percentages],
            "monetary_amounts": [m.model_dump() for m in self.monetary_amounts]
        }
    
    def count_total(self) -> int:
        """Get total count of all quantitative elements."""
        return (len(self.standards) + len(self.thresholds) + 
                len(self.percentages) + len(self.monetary_amounts))


class QuantitativeExtractionResult(BaseModel):
    """Result of quantitative extraction."""
    
    content: QuantitativeContent
    processing_time: float = Field(..., description="Processing time in seconds")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "content": self.content.to_dict(),
            "processing_time": self.processing_time,
            "total_elements": self.content.count_total()
        }

# Made with Bob
