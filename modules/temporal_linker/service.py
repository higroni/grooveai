"""
Temporal Linker Service - Links temporal elements to normative statements.

This module extracts temporal elements (deadlines, durations, dates) and links them
to obligations, prohibitions, and permissions.
"""

import re
import time
from typing import List, Dict, Any, Optional
from .models import (
    TemporalElement, LinkedObligation, LinkedProhibition, LinkedPermission,
    TemporalLinkingResult
)


class TemporalLinker:
    """
    Links temporal elements to normative statements.
    """
    
    # Temporal patterns
    DEADLINE_PATTERNS = [
        # "u roku od X dana"
        r'u\s+roku\s+od\s+(\d+)\s+(dana|meseci|godina)',
        # "do X dana"
        r'do\s+(\d+)\s+(dana|meseci|godina)',
        # "najkasnije do"
        r'najkasnije\s+do\s+([^,.;!?]+)',
        # "u roku koji ne može biti duži od"
        r'u\s+roku\s+koji\s+ne\s+može\s+biti\s+duži\s+od\s+(\d+)\s+(dana|meseci|godina)',
    ]
    
    DURATION_PATTERNS = [
        # "tokom X dana/meseci/godina"
        r'tokom\s+(\d+)\s+(dana|meseci|godina)',
        # "u periodu od X do Y"
        r'u\s+periodu\s+od\s+(\d+)\s+do\s+(\d+)\s+(dana|meseci|godina)',
        # "najmanje X dana"
        r'najmanje\s+(\d+)\s+(dana|meseci|godina)',
        # "najviše X dana"
        r'najviše\s+(\d+)\s+(dana|meseci|godina)',
    ]
    
    EFFECTIVE_DATE_PATTERNS = [
        # "stupa na snagu"
        r'stupa\s+na\s+snagu\s+([^,.;!?]+)',
        # "primenjuje se od"
        r'primenjuje\s+se\s+od\s+([^,.;!?]+)',
        # "važi od"
        r'važi\s+od\s+([^,.;!?]+)',
    ]
    
    REFERENCE_POINT_PATTERNS = [
        # "od dana dostavljanja"
        r'od\s+dana\s+([a-zšđčćž]+)',
        # "od momenta"
        r'od\s+momenta\s+([^,.;!?]+)',
        # "nakon"
        r'nakon\s+([^,.;!?]+)',
    ]
    
    def __init__(self):
        """Initialize the temporal linker."""
        # Compile patterns for better performance
        self.deadline_patterns = [re.compile(p, re.IGNORECASE) for p in self.DEADLINE_PATTERNS]
        self.duration_patterns = [re.compile(p, re.IGNORECASE) for p in self.DURATION_PATTERNS]
        self.effective_date_patterns = [re.compile(p, re.IGNORECASE) for p in self.EFFECTIVE_DATE_PATTERNS]
        self.reference_point_patterns = [re.compile(p, re.IGNORECASE) for p in self.REFERENCE_POINT_PATTERNS]
    
    def extract_temporal_elements(self, text: str) -> List[TemporalElement]:
        """
        Extract temporal elements from text.
        
        Args:
            text: Input text
            
        Returns:
            List of TemporalElement objects
        """
        elements = []
        
        # Extract deadlines
        for pattern in self.deadline_patterns:
            for match in pattern.finditer(text):
                element = TemporalElement(
                    type='deadline',
                    value=match.group(0),
                    reference_point=self._extract_reference_point(text, match.start()),
                    is_mandatory=True,
                    can_be_extended='najkasnije' not in match.group(0).lower(),
                    applies_to=None,
                    source_text=match.group(0),
                    confidence=0.9
                )
                elements.append(element)
        
        # Extract durations
        for pattern in self.duration_patterns:
            for match in pattern.finditer(text):
                element = TemporalElement(
                    type='duration',
                    value=match.group(0),
                    reference_point=None,
                    is_mandatory='najmanje' in match.group(0).lower() or 'najviše' in match.group(0).lower(),
                    applies_to=None,
                    source_text=match.group(0),
                    confidence=0.9
                )
                elements.append(element)
        
        # Extract effective dates
        for pattern in self.effective_date_patterns:
            for match in pattern.finditer(text):
                element = TemporalElement(
                    type='effective_date',
                    value=match.group(0),
                    reference_point=None,
                    is_mandatory=True,
                    applies_to=None,
                    source_text=match.group(0),
                    confidence=0.8
                )
                elements.append(element)
        
        return elements
    
    def _extract_reference_point(self, text: str, position: int) -> Optional[str]:
        """
        Extract reference point for a temporal element.
        
        Args:
            text: Full text
            position: Position of temporal element
            
        Returns:
            Reference point string or None
        """
        # Look in surrounding context (50 chars before and after)
        context_start = max(0, position - 50)
        context_end = min(len(text), position + 100)
        context = text[context_start:context_end]
        
        for pattern in self.reference_point_patterns:
            match = pattern.search(context)
            if match:
                return match.group(0)
        
        return None
    
    def link_temporal_to_obligations(
        self,
        obligations: List[Dict[str, Any]],
        temporal_elements: List[TemporalElement]
    ) -> List[LinkedObligation]:
        """
        Link temporal elements to obligations.
        
        Args:
            obligations: List of obligation dictionaries
            temporal_elements: List of temporal elements
            
        Returns:
            List of LinkedObligation objects
        """
        linked = []
        
        for obl in obligations:
            # Find temporal elements in obligation's source text
            obl_temporals = []
            for temp in temporal_elements:
                if temp.source_text in obl['source_text']:
                    temp.applies_to = f"obligation_{obligations.index(obl)}"
                    obl_temporals.append(temp)
            
            linked_obl = LinkedObligation(
                subject=obl['subject'],
                action=obl['action'],
                object=obl.get('object'),
                modality=obl['modality'],
                condition=obl.get('condition'),
                temporal_elements=obl_temporals,
                source_text=obl['source_text'],
                confidence=obl['confidence']
            )
            linked.append(linked_obl)
        
        return linked
    
    def link_temporal_to_prohibitions(
        self,
        prohibitions: List[Dict[str, Any]],
        temporal_elements: List[TemporalElement]
    ) -> List[LinkedProhibition]:
        """
        Link temporal elements to prohibitions.
        
        Args:
            prohibitions: List of prohibition dictionaries
            temporal_elements: List of temporal elements
            
        Returns:
            List of LinkedProhibition objects
        """
        linked = []
        
        for proh in prohibitions:
            # Find temporal elements in prohibition's source text
            proh_temporals = []
            for temp in temporal_elements:
                if temp.source_text in proh['source_text']:
                    temp.applies_to = f"prohibition_{prohibitions.index(proh)}"
                    proh_temporals.append(temp)
            
            linked_proh = LinkedProhibition(
                subject=proh['subject'],
                action=proh['action'],
                object=proh.get('object'),
                modality=proh['modality'],
                exception=proh.get('exception'),
                temporal_elements=proh_temporals,
                source_text=proh['source_text'],
                confidence=proh['confidence']
            )
            linked.append(linked_proh)
        
        return linked
    
    def link_temporal_to_permissions(
        self,
        permissions: List[Dict[str, Any]],
        temporal_elements: List[TemporalElement]
    ) -> List[LinkedPermission]:
        """
        Link temporal elements to permissions.
        
        Args:
            permissions: List of permission dictionaries
            temporal_elements: List of temporal elements
            
        Returns:
            List of LinkedPermission objects
        """
        linked = []
        
        for perm in permissions:
            # Find temporal elements in permission's source text
            perm_temporals = []
            for temp in temporal_elements:
                if temp.source_text in perm['source_text']:
                    temp.applies_to = f"permission_{permissions.index(perm)}"
                    perm_temporals.append(temp)
            
            linked_perm = LinkedPermission(
                subject=perm['subject'],
                action=perm['action'],
                object=perm.get('object'),
                modality=perm['modality'],
                condition=perm.get('condition'),
                temporal_elements=perm_temporals,
                source_text=perm['source_text'],
                confidence=perm['confidence']
            )
            linked.append(linked_perm)
        
        return linked
    
    def link_temporal_elements(
        self,
        text: str,
        normative_content: Dict[str, Any]
    ) -> TemporalLinkingResult:
        """
        Extract temporal elements and link them to normative content.
        
        Args:
            text: Input text
            normative_content: Dictionary with obligations, prohibitions, permissions
            
        Returns:
            TemporalLinkingResult with linked elements
        """
        start_time = time.time()
        
        # Extract temporal elements
        temporal_elements = self.extract_temporal_elements(text)
        
        # Link to obligations
        linked_obligations = self.link_temporal_to_obligations(
            normative_content.get('obligations', []),
            temporal_elements
        )
        
        # Link to prohibitions
        linked_prohibitions = self.link_temporal_to_prohibitions(
            normative_content.get('prohibitions', []),
            temporal_elements
        )
        
        # Link to permissions
        linked_permissions = self.link_temporal_to_permissions(
            normative_content.get('permissions', []),
            temporal_elements
        )
        
        # Find unlinked temporal elements
        linked_ids = set()
        for obl in linked_obligations:
            for temp in obl.temporal_elements:
                if temp.applies_to:
                    linked_ids.add(temp.applies_to)
        
        unlinked = [t for t in temporal_elements if not t.applies_to]
        
        processing_time = time.time() - start_time
        
        return TemporalLinkingResult(
            linked_obligations=linked_obligations,
            linked_prohibitions=linked_prohibitions,
            linked_permissions=linked_permissions,
            unlinked_temporal_elements=unlinked,
            processing_time=processing_time
        )


# Singleton instance
_linker = None

def get_linker() -> TemporalLinker:
    """Get singleton linker instance."""
    global _linker
    if _linker is None:
        _linker = TemporalLinker()
    return _linker


def link_temporal_elements(text: str, normative_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Link temporal elements to normative content.
    
    Args:
        text: Input text
        normative_content: Dictionary with obligations, prohibitions, permissions
        
    Returns:
        Dictionary with linked temporal elements
    """
    linker = get_linker()
    result = linker.link_temporal_elements(text, normative_content)
    return result.to_dict()

# Made with Bob
