"""
Data models for Procedural Extractor module.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class ProceduralStep(BaseModel):
    """Represents a single step in a procedure."""
    
    step_number: Optional[int] = Field(None, description="Step number in sequence")
    action: str = Field(..., description="Action to be performed")
    actor: Optional[str] = Field(None, description="Who performs the action")
    deadline: Optional[str] = Field(None, description="Time constraint for the step")
    context: str = Field(..., description="Full context of the step")
    line_number: Optional[int] = Field(None, description="Line number in source")


class Sequence(BaseModel):
    """Represents a sequence of steps."""
    
    sequence_type: str = Field(..., description="Type: 'ordered', 'parallel', 'conditional'")
    steps: List[ProceduralStep] = Field(default_factory=list)
    description: Optional[str] = Field(None, description="Description of the sequence")


class Actor(BaseModel):
    """Represents an actor/participant in procedures."""
    
    name: str = Field(..., description="Name or role of the actor")
    role: Optional[str] = Field(None, description="Role description")
    responsibilities: List[str] = Field(default_factory=list)
    context: str = Field(..., description="Context where actor appears")
    line_number: Optional[int] = Field(None, description="Line number in source")


class Dependency(BaseModel):
    """Represents a dependency between steps."""
    
    step_from: str = Field(..., description="Source step")
    step_to: str = Field(..., description="Target step")
    dependency_type: str = Field(..., description="Type: 'prerequisite', 'follows', 'blocks'")
    context: str = Field(..., description="Context of the dependency")


class ApprovalAuthority(BaseModel):
    """Represents an approval authority requirement."""
    
    authority: str = Field(..., description="Name of the approval authority")
    approval_type: str = Field(..., description="Type: 'consent', 'approval', 'authorization', 'permit'")
    required_for: str = Field(..., description="What requires approval")
    conditions: Optional[str] = Field(None, description="Conditions for approval")
    context: str = Field(..., description="Full context")
    line_number: Optional[int] = Field(None, description="Line number in source")


class DocumentationRequirement(BaseModel):
    """Represents a documentation requirement."""
    
    document_type: str = Field(..., description="Type of document required")
    required_by: Optional[str] = Field(None, description="Who must provide the document")
    purpose: Optional[str] = Field(None, description="Purpose of the document")
    deadline: Optional[str] = Field(None, description="Deadline for submission")
    context: str = Field(..., description="Full context")
    line_number: Optional[int] = Field(None, description="Line number in source")


class FormRequirement(BaseModel):
    """Represents a form requirement."""
    
    form_name: str = Field(..., description="Name or type of form")
    form_purpose: str = Field(..., description="Purpose of the form")
    mandatory: bool = Field(default=True, description="Whether form is mandatory")
    prescribed_by: Optional[str] = Field(None, description="Who prescribes the form")
    context: str = Field(..., description="Full context")
    line_number: Optional[int] = Field(None, description="Line number in source")


class ProceduralContent(BaseModel):
    """Container for all procedural content."""
    
    steps: List[ProceduralStep] = Field(default_factory=list)
    sequences: List[Sequence] = Field(default_factory=list)
    actors: List[Actor] = Field(default_factory=list)
    dependencies: List[Dependency] = Field(default_factory=list)
    approval_authorities: List[ApprovalAuthority] = Field(default_factory=list)
    documentation_requirements: List[DocumentationRequirement] = Field(default_factory=list)
    form_requirements: List[FormRequirement] = Field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "steps": [s.model_dump() for s in self.steps],
            "sequences": [s.model_dump() for s in self.sequences],
            "actors": [a.model_dump() for a in self.actors],
            "dependencies": [d.model_dump() for d in self.dependencies],
            "approval_authorities": [a.model_dump() for a in self.approval_authorities],
            "documentation_requirements": [d.model_dump() for d in self.documentation_requirements],
            "form_requirements": [f.model_dump() for f in self.form_requirements]
        }
    
    def count_total(self) -> int:
        """Get total count of all procedural elements."""
        return (len(self.steps) + len(self.sequences) +
                len(self.actors) + len(self.dependencies) +
                len(self.approval_authorities) + len(self.documentation_requirements) +
                len(self.form_requirements))


class ProceduralExtractionResult(BaseModel):
    """Result of procedural extraction."""
    
    content: ProceduralContent
    processing_time: float = Field(..., description="Processing time in seconds")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "content": self.content.to_dict(),
            "processing_time": self.processing_time,
            "total_elements": self.content.count_total()
        }

# Made with Bob
