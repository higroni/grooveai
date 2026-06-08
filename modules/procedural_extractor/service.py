"""
Procedural Extractor Service - Extracts procedural steps, sequences, and actors.

This module extracts procedural information including steps, sequences, actors,
and dependencies from legal text.
"""

import re
import time
from typing import List, Optional, Tuple
from .models import (
    ProceduralStep, Sequence, Actor, Dependency,
    ApprovalAuthority, DocumentationRequirement, FormRequirement,
    ProceduralContent, ProceduralExtractionResult
)


class ProceduralExtractor:
    """
    Extracts procedural content from legal text.
    """
    
    # Step patterns
    STEP_PATTERNS = [
        r'(\d+)\)\s+([^,.;!?]+?(?:podnosi|dostavlja|izdaje|donosi|obaveštava|sastavlja|vrši|sprovodi)[^,.;!?]+?[,.;!?])',
        r'korak\s+(\d+)[:\s]+([^,.;!?]+?[,.;!?])',
        r'faza\s+(\d+)[:\s]+([^,.;!?]+?[,.;!?])',
    ]
    
    # Action patterns (verbs indicating procedural actions)
    ACTION_PATTERNS = [
        r'(podnosi|podnese)[^,.;!?]+?[,.;!?]',
        r'(dostavlja|dostavi)[^,.;!?]+?[,.;!?]',
        r'(izdaje|izda)[^,.;!?]+?[,.;!?]',
        r'(donosi|donese)[^,.;!?]+?[,.;!?]',
        r'(obaveštava|obavesti)[^,.;!?]+?[,.;!?]',
        r'(sastavlja|sastavi)[^,.;!?]+?[,.;!?]',
        r'(vrši|izvrši)[^,.;!?]+?[,.;!?]',
        r'(sprovodi|sprovede)[^,.;!?]+?[,.;!?]',
        r'(podnosi zahtev)[^,.;!?]+?[,.;!?]',
        r'(podnosi prijavu)[^,.;!?]+?[,.;!?]',
        r'(podnosi žalbu)[^,.;!?]+?[,.;!?]',
    ]
    
    # Actor patterns
    ACTOR_PATTERNS = [
        r'(poslodavac|Poslodavac)[^,.;!?]+?[,.;!?]',
        r'(zaposleni|Zaposleni)[^,.;!?]+?[,.;!?]',
        r'(radnik|Radnik)[^,.;!?]+?[,.;!?]',
        r'(ministar|Ministar)[^,.;!?]+?[,.;!?]',
        r'(direktor|Direktor)[^,.;!?]+?[,.;!?]',
        r'(inspektor|Inspektor)[^,.;!?]+?[,.;!?]',
        r'(organ|Organ)[^,.;!?]+?[,.;!?]',
        r'(komisija|Komisija)[^,.;!?]+?[,.;!?]',
        r'(sud|Sud)[^,.;!?]+?[,.;!?]',
    ]
    
    # Sequence indicators
    SEQUENCE_PATTERNS = [
        r'prvo[^,.;!?]+?[,.;!?]',
        r'drugo[^,.;!?]+?[,.;!?]',
        r'treće[^,.;!?]+?[,.;!?]',
        r'zatim[^,.;!?]+?[,.;!?]',
        r'nakon toga[^,.;!?]+?[,.;!?]',
        r'potom[^,.;!?]+?[,.;!?]',
        r'na kraju[^,.;!?]+?[,.;!?]',
    ]
    
    # Dependency patterns
    DEPENDENCY_PATTERNS = [
        r'pre nego što[^,.;!?]+?[,.;!?]',
        r'nakon što[^,.;!?]+?[,.;!?]',
        r'po izvršenju[^,.;!?]+?[,.;!?]',
        r'po prijemu[^,.;!?]+?[,.;!?]',
        r'po dostavljanju[^,.;!?]+?[,.;!?]',
    ]
    
    # Deadline patterns (for steps)
    DEADLINE_PATTERNS = [
        r'u roku od\s+(\d+)\s+(dan[a]?|mesec[i]?|godin[e]?)',
        r'najkasnije\s+(\d+)\s+(dan[a]?|mesec[i]?|godin[e]?)',
        r'u\s+(\d+)\s+(dan[a]?|mesec[i]?|godin[e]?)',
    ]
    
    # Approval authority patterns
    APPROVAL_PATTERNS = [
        r'(uz\s+saglasnost|sa\s+saglasn(?:ošću|osti))\s+([^,.;!?]+?)[,.;!?]',
        r'(uz\s+odobrenje|sa\s+odobrenj(?:em|a))\s+([^,.;!?]+?)[,.;!?]',
        r'(uz\s+dozvolu)\s+([^,.;!?]+?)[,.;!?]',
        r'(odobrava|odobri)\s+([^,.;!?]+?)[,.;!?]',
        r'(daje\s+saglasnost)\s+([^,.;!?]+?)[,.;!?]',
        r'(izdaje\s+dozvolu)\s+([^,.;!?]+?)[,.;!?]',
        r'(zahteva\s+saglasnost)\s+([^,.;!?]+?)[,.;!?]',
    ]
    
    # Documentation requirement patterns
    DOCUMENTATION_PATTERNS = [
        r'(podnosi|dostavlja|prilaže)\s+(dokaz|potvrdu|uverenje|izveštaj|zapisnik|dokument)[^,.;!?]+?[,.;!?]',
        r'(uz\s+zahtev\s+se\s+prilaže)\s+([^,.;!?]+?)[,.;!?]',
        r'(potrebno\s+je\s+dostaviti)\s+([^,.;!?]+?)[,.;!?]',
        r'(obavezan\s+je\s+da\s+dostavi)\s+([^,.;!?]+?)[,.;!?]',
        r'(mora\s+priložiti)\s+([^,.;!?]+?)[,.;!?]',
    ]
    
    # Form requirement patterns
    FORM_PATTERNS = [
        r'(na\s+propisanom\s+obrascu)[^,.;!?]+?[,.;!?]',
        r'(obrazac\s+broj)\s+([^,.;!?]+?)[,.;!?]',
        r'(popunjava\s+obrazac)[^,.;!?]+?[,.;!?]',
        r'(u\s+formi\s+propisanoj)\s+([^,.;!?]+?)[,.;!?]',
        r'(ministar\s+propisuje\s+obrazac)[^,.;!?]+?[,.;!?]',
        r'(obrazac\s+iz\s+stava)[^,.;!?]+?[,.;!?]',
    ]
    
    def __init__(self):
        """Initialize the extractor."""
        # Compile patterns for better performance
        self.step_patterns = [re.compile(p, re.IGNORECASE) for p in self.STEP_PATTERNS]
        self.action_patterns = [re.compile(p, re.IGNORECASE) for p in self.ACTION_PATTERNS]
        self.actor_patterns = [re.compile(p, re.IGNORECASE) for p in self.ACTOR_PATTERNS]
        self.sequence_patterns = [re.compile(p, re.IGNORECASE) for p in self.SEQUENCE_PATTERNS]
        self.dependency_patterns = [re.compile(p, re.IGNORECASE) for p in self.DEPENDENCY_PATTERNS]
        self.deadline_patterns = [re.compile(p, re.IGNORECASE) for p in self.DEADLINE_PATTERNS]
        self.approval_patterns = [re.compile(p, re.IGNORECASE) for p in self.APPROVAL_PATTERNS]
        self.documentation_patterns = [re.compile(p, re.IGNORECASE) for p in self.DOCUMENTATION_PATTERNS]
        self.form_patterns = [re.compile(p, re.IGNORECASE) for p in self.FORM_PATTERNS]
    
    def extract_deadline(self, text: str) -> Optional[str]:
        """
        Extract deadline from text.
        
        Args:
            text: Input text
            
        Returns:
            Deadline string or None
        """
        for pattern in self.deadline_patterns:
            match = pattern.search(text)
            if match:
                return match.group(0)
        return None
    
    def extract_actor_from_context(self, text: str) -> Optional[str]:
        """
        Extract actor from context.
        
        Args:
            text: Input text
            
        Returns:
            Actor name or None
        """
        for pattern in self.actor_patterns:
            match = pattern.search(text)
            if match:
                return match.group(1)
        return None
    
    def extract_steps(self, text: str) -> List[ProceduralStep]:
        """
        Extract procedural steps.
        
        Args:
            text: Input text
            
        Returns:
            List of ProceduralStep objects
        """
        steps = []
        lines = text.split('\n')
        
        # Extract numbered steps
        for pattern in self.step_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    step_num = int(match.group(1)) if match.group(1).isdigit() else None
                    action = match.group(2).strip()
                    context = match.group(0).strip()
                    
                    actor = self.extract_actor_from_context(context)
                    deadline = self.extract_deadline(context)
                    
                    steps.append(ProceduralStep(
                        step_number=step_num,
                        action=action,
                        actor=actor,
                        deadline=deadline,
                        context=context,
                        line_number=line_num
                    ))
        
        # Extract action-based steps (without explicit numbering)
        for pattern in self.action_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    action = match.group(0).strip()
                    context = match.group(0).strip()
                    
                    # Skip if already captured as numbered step
                    if any(s.context == context for s in steps):
                        continue
                    
                    actor = self.extract_actor_from_context(context)
                    deadline = self.extract_deadline(context)
                    
                    steps.append(ProceduralStep(
                        step_number=None,
                        action=action,
                        actor=actor,
                        deadline=deadline,
                        context=context,
                        line_number=line_num
                    ))
        
        return steps
    
    def extract_actors(self, text: str) -> List[Actor]:
        """
        Extract actors/participants.
        
        Args:
            text: Input text
            
        Returns:
            List of Actor objects
        """
        actors = []
        lines = text.split('\n')
        actor_map = {}  # Track unique actors
        
        for pattern in self.actor_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    actor_name = match.group(1)
                    context = match.group(0).strip()
                    
                    # Add to actor map or update responsibilities
                    if actor_name.lower() not in actor_map:
                        actor_map[actor_name.lower()] = Actor(
                            name=actor_name,
                            role=None,
                            responsibilities=[context],
                            context=context,
                            line_number=line_num
                        )
                    else:
                        # Add responsibility if not duplicate
                        if context not in actor_map[actor_name.lower()].responsibilities:
                            actor_map[actor_name.lower()].responsibilities.append(context)
        
        return list(actor_map.values())
    
    def extract_sequences(self, text: str, steps: List[ProceduralStep]) -> List[Sequence]:
        """
        Extract sequences from text and steps.
        
        Args:
            text: Input text
            steps: List of extracted steps
            
        Returns:
            List of Sequence objects
        """
        sequences = []
        
        # Check for sequence indicators
        has_sequence_indicators = any(
            pattern.search(text) for pattern in self.sequence_patterns
        )
        
        if has_sequence_indicators:
            # Create ordered sequence from steps
            ordered_steps = [s for s in steps if s.step_number is not None]
            if ordered_steps:
                ordered_steps.sort(key=lambda x: x.step_number or 0)
                sequences.append(Sequence(
                    sequence_type="ordered",
                    steps=ordered_steps,
                    description="Ordered procedural sequence"
                ))
        
        return sequences
    
    def extract_dependencies(self, text: str, steps: List[ProceduralStep]) -> List[Dependency]:
        """
        Extract dependencies between steps.
        
        Args:
            text: Input text
            steps: List of extracted steps
            
        Returns:
            List of Dependency objects
        """
        dependencies = []
        
        for pattern in self.dependency_patterns:
            for match in pattern.finditer(text):
                context = match.group(0).strip()
                
                # Determine dependency type
                dep_type = "prerequisite"
                if "nakon što" in context.lower() or "po izvršenju" in context.lower():
                    dep_type = "follows"
                elif "pre nego što" in context.lower():
                    dep_type = "prerequisite"
                
                dependencies.append(Dependency(
                    step_from="unknown",
                    step_to="unknown",
                    dependency_type=dep_type,
                    context=context
                ))
        
        return dependencies
    
    def extract_approval_authorities(self, text: str) -> List[ApprovalAuthority]:
        """
        Extract approval authority requirements.
        
        Args:
            text: Input text
            
        Returns:
            List of ApprovalAuthority objects
        """
        authorities = []
        lines = text.split('\n')
        
        for pattern in self.approval_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    context = match.group(0).strip()
                    
                    # Determine approval type
                    approval_type = "consent"
                    if "odobrenje" in context.lower() or "odobrava" in context.lower():
                        approval_type = "approval"
                    elif "dozvola" in context.lower() or "izdaje dozvolu" in context.lower():
                        approval_type = "permit"
                    elif "saglasnost" in context.lower():
                        approval_type = "consent"
                    
                    # Extract authority name (group 2 if exists)
                    authority_name = match.group(2).strip() if len(match.groups()) > 1 else "Unknown"
                    
                    # Extract what requires approval
                    required_for = context
                    
                    authorities.append(ApprovalAuthority(
                        authority=authority_name,
                        approval_type=approval_type,
                        required_for=required_for,
                        conditions=None,
                        context=context,
                        line_number=line_num
                    ))
        
        return authorities
    
    def extract_documentation_requirements(self, text: str) -> List[DocumentationRequirement]:
        """
        Extract documentation requirements.
        
        Args:
            text: Input text
            
        Returns:
            List of DocumentationRequirement objects
        """
        requirements = []
        lines = text.split('\n')
        
        for pattern in self.documentation_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    context = match.group(0).strip()
                    
                    # Extract document type
                    doc_type = "document"
                    if "dokaz" in context.lower():
                        doc_type = "proof"
                    elif "potvrda" in context.lower():
                        doc_type = "certificate"
                    elif "uverenje" in context.lower():
                        doc_type = "attestation"
                    elif "izveštaj" in context.lower():
                        doc_type = "report"
                    elif "zapisnik" in context.lower():
                        doc_type = "minutes"
                    
                    # Extract who must provide
                    required_by = self.extract_actor_from_context(context)
                    
                    # Extract deadline
                    deadline = self.extract_deadline(context)
                    
                    requirements.append(DocumentationRequirement(
                        document_type=doc_type,
                        required_by=required_by,
                        purpose=None,
                        deadline=deadline,
                        context=context,
                        line_number=line_num
                    ))
        
        return requirements
    
    def extract_form_requirements(self, text: str) -> List[FormRequirement]:
        """
        Extract form requirements.
        
        Args:
            text: Input text
            
        Returns:
            List of FormRequirement objects
        """
        forms = []
        lines = text.split('\n')
        
        for pattern in self.form_patterns:
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    context = match.group(0).strip()
                    
                    # Extract form name
                    form_name = "prescribed form"
                    if "obrazac broj" in context.lower():
                        form_name = match.group(2).strip() if len(match.groups()) > 1 else "numbered form"
                    elif "propisanom obrascu" in context.lower():
                        form_name = "prescribed form"
                    
                    # Determine if mandatory
                    mandatory = "mora" in context.lower() or "obavezan" in context.lower() or "propisanom" in context.lower()
                    
                    # Extract who prescribes
                    prescribed_by = None
                    if "ministar propisuje" in context.lower():
                        prescribed_by = "Minister"
                    
                    # Extract purpose
                    purpose = context
                    
                    forms.append(FormRequirement(
                        form_name=form_name,
                        form_purpose=purpose,
                        mandatory=mandatory,
                        prescribed_by=prescribed_by,
                        context=context,
                        line_number=line_num
                    ))
        
        return forms
    
    def extract(self, text: str) -> ProceduralExtractionResult:
        """
        Extract all procedural content.
        
        Args:
            text: Input text
            
        Returns:
            ProceduralExtractionResult
        """
        start_time = time.time()
        
        # Extract all types
        steps = self.extract_steps(text)
        actors = self.extract_actors(text)
        sequences = self.extract_sequences(text, steps)
        dependencies = self.extract_dependencies(text, steps)
        approval_authorities = self.extract_approval_authorities(text)
        documentation_requirements = self.extract_documentation_requirements(text)
        form_requirements = self.extract_form_requirements(text)
        
        content = ProceduralContent(
            steps=steps,
            sequences=sequences,
            actors=actors,
            dependencies=dependencies,
            approval_authorities=approval_authorities,
            documentation_requirements=documentation_requirements,
            form_requirements=form_requirements
        )
        
        processing_time = time.time() - start_time
        
        return ProceduralExtractionResult(
            content=content,
            processing_time=processing_time
        )


# Singleton instance
_extractor = None

def get_extractor() -> ProceduralExtractor:
    """Get singleton extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = ProceduralExtractor()
    return _extractor


def extract_procedural(text: str) -> dict:
    """
    Extract procedural content from text.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with extraction result
    """
    extractor = get_extractor()
    result = extractor.extract(text)
    return result.to_dict()

# Made with Bob
