"""
Normative Extractor Service - Extracts obligations, prohibitions, permissions, and definitions.

This module uses regex pattern matching to extract normative content from legal text.
"""

import re
import time
from typing import List, Optional, Dict, Any
from .models import (
    Obligation, Prohibition, Permission, Definition,
    Waiver, Transfer, Assignment, AmbiguityScore, CircularDefinition,
    NormativeContent, ExtractionResult
)


class NormativeExtractor:
    """
    Extracts normative content (obligations, prohibitions, permissions, definitions)
    from legal text using regex pattern matching.
    """
    
    # Obligation patterns - "dužan je", "mora", "obavezan je" + sinonimi
    OBLIGATION_PATTERNS = [
        # Pattern: Subject + dužan je + action + object + temporal (capture until sentence end)
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>dužan\s+je|mora|obavezan\s+je|dužan\s+da|obavezan\s+da|u\s+obavezi\s+je|potrebno\s+je\s+da|nužno\s+je\s+da|neophodno\s+je\s+da)\s+(?:da\s+)?(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)(?:\s+(?P<temporal>u\s+roku\s+od\s+\d+\s+dana[^,.;!?]*|do\s+[^,.;!?]+))?[,.;!?]',
        
        # Pattern: Subject + ima obavezu + action + object (capture until sentence end)
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>ima\s+obavezu|ima\s+dužnost|snosi\s+obavezu|podleže\s+obavezi)\s+(?:da\s+)?(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Obaveza + subject + action + object
        r'(?P<modality>Obaveza|Dužnost)\s+(?P<subject>[a-zšđčćž]+(?:\s+[a-zšđčćž]+)*?)\s+je\s+(?:da\s+)?(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Subject + treba da + action
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>treba\s+da|potrebno\s+je\s+da)\s+(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Subject + je u obavezi da + action
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+je\s+(?P<modality>u\s+obavezi\s+da|u\s+dužnosti\s+da)\s+(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
    ]
    
    # Prohibition patterns - "zabranjeno je", "ne može", "ne sme" + sinonimi
    PROHIBITION_PATTERNS = [
        # Pattern: Subject + ne sme/ne može + action + object (capture until sentence end)
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>ne\s+sme|ne\s+može|nije\s+dozvoljeno|nije\s+dopušteno|nema\s+pravo)\s+(?:da\s+)?(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Zabranjeno je + action + object (capture until sentence end)
        r'(?P<modality>Zabranjeno\s+je|Zabranjen\s+je|Zabranjena\s+je|Nije\s+dozvoljeno|Nije\s+dopušteno|Nedopušteno\s+je)\s+(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Subject + zabranjeno + action + object
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+je\s+(?P<modality>zabranjeno|nedopušteno|isključeno)\s+(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Subject + nema pravo da + action
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>nema\s+pravo\s+da|nije\s+ovlašćen\s+da)\s+(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Zabrana + action
        r'(?P<modality>Zabrana)\s+(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
    ]
    
    # Permission patterns - "može", "ima pravo", "dozvoljeno je" + sinonimi
    PERMISSION_PATTERNS = [
        # Pattern: Subject + može + action + object + condition (capture until sentence end)
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>može|u\s+mogućnosti\s+je|slobodan\s+je|ovlašćen\s+je)\s+(?:da\s+)?(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)(?:\s+(?P<condition>(?:ako|ukoliko|pod\s+uslovom)[^,.;!?]+))?[,.;!?]',
        
        # Pattern: Subject + ima pravo + action + object (capture until sentence end)
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>ima\s+pravo|ima\s+ovlašćenje|ima\s+mogućnost|ovlašćen\s+je)\s+(?:da\s+)?(?:(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)|na\s+(?P<object2>[^,.;!?]+?))[,.;!?]',
        
        # Pattern: Dozvoljeno je + action + object
        r'(?P<modality>Dozvoljeno\s+je|Dozvoljen\s+je|Dozvoljena\s+je|Dopušteno\s+je|Dopušten\s+je|Dopuštena\s+je)\s+(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Subject + slobodan je da + action
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+je\s+(?P<modality>slobodan\s+da|u\s+pravu\s+da)\s+(?P<action>[a-zšđčćž]+)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
    ]
    
    # Definition patterns - "smatra se", "u smislu ovog zakona" + sinonimi
    DEFINITION_PATTERNS = [
        # Pattern: Term + smatra se + definition (capture until sentence end or scope)
        r'(?P<term>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+se\s+(?P<modality>smatra|računa|uzima)\s+(?P<definition>[^,.;!?]+?)(?:\s+(?P<scope>u\s+smislu\s+ovog\s+zakona|u\s+smislu\s+ovog\s+pravilnika|u\s+smislu\s+ove\s+uredbe))?[,.;!?]',
        
        # Pattern: U smislu ovog zakona, term je definition (capture until sentence end)
        r'(?P<scope>U\s+smislu\s+ovog\s+zakona|U\s+smislu\s+ovog\s+pravilnika|U\s+smislu\s+ove\s+uredbe|Za\s+potrebe\s+ovog\s+zakona),?\s+(?P<term>[a-zšđčćž]+(?:\s+[a-zšđčćž]+)*?)\s+(?:je|su|predstavlja|označava)\s+(?P<definition>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Term je definition (u smislu ovog zakona)
        r'(?P<term>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?:je|su|predstavlja|označava)\s+(?P<definition>[^()]+?)\s+\((?P<scope>u\s+smislu\s+ovog\s+zakona|u\s+smislu\s+ovog\s+pravilnika|u\s+smislu\s+ove\s+uredbe)\)',
        
        # Pattern: Pod terminom "X" podrazumeva se Y (capture until sentence end)
        r'Pod\s+(?:terminom|pojmom|nazivom)\s+"(?P<term>[^"]+)"\s+(?P<modality>podrazumeva\s+se|smatra\s+se|misli\s+se)\s+(?P<definition>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Term znači definition
        r'(?P<term>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>znači|označava|predstavlja)\s+(?P<definition>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Pojam term obuhvata definition
        r'(?:Pojam|Termin|Naziv)\s+(?P<term>[a-zšđčćž]+(?:\s+[a-zšđčćž]+)*?)\s+(?P<modality>obuhvata|uključuje)\s+(?P<definition>[^,.;!?]+?)[,.;!?]',
    ]
    
    # Waiver patterns - "odriče se prava", "ne može se odreći" + sinonimi
    WAIVER_PATTERNS = [
        # Pattern: Subject + odriče se prava na + object
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>odriče\s+se\s+prava|odriče\s+se|odustaje\s+od\s+prava)\s+na\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Odricanje od prava + object
        r'(?P<modality>Odricanje\s+od\s+prava|Odustajanje\s+od\s+prava)\s+na\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Ne može se odreći + object
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>ne\s+može\s+se\s+odreći|nije\s+moguće\s+odreći\s+se|ne\s+može\s+odustati)\s+(?:prava\s+na\s+)?(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Odricanje je ništavo
        r'(?P<modality>Odricanje|Odustajanje)\s+(?:od\s+prava\s+na\s+)?(?P<object>[^,.;!?]+?)\s+je\s+(?P<validity>ništavo|nevažeće|bez\s+pravnog\s+dejstva)[,.;!?]',
        
        # Pattern: Subject se odriče + object
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+se\s+(?P<modality>odriče|odustaje\s+od)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
    ]
    
    # Transfer patterns - "prenosi se na", "prelazi na" + sinonimi
    TRANSFER_PATTERNS = [
        # Pattern: Subject + prenosi + object + na + recipient
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>prenosi|preusmerava|prebacuje)\s+(?P<object>[^,.;!?]+?)\s+na\s+(?P<recipient>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Object + se prenosi na + recipient
        r'(?P<object>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+se\s+(?P<modality>prenosi|preusmerava|prebacuje|prenosi)\s+na\s+(?P<recipient>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Object + prelazi na + recipient
        r'(?P<object>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>prelazi|prelazi|prelazi)\s+na\s+(?P<recipient>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Ne može se preneti + object
        r'(?P<modality>Ne\s+može\s+se\s+preneti|Nije\s+moguće\s+preneti|Zabranjeno\s+je\s+prenošenje)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Prenos + object + na + recipient
        r'(?P<modality>Prenos|Preusmeravanje)\s+(?P<object>[^,.;!?]+?)\s+na\s+(?P<recipient>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Object + se prenosi sa + from + na + to
        r'(?P<object>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+se\s+(?P<modality>prenosi|prebacuje)\s+sa\s+(?P<from>[^,.;!?]+?)\s+na\s+(?P<recipient>[^,.;!?]+?)[,.;!?]',
    ]
    
    # Assignment patterns - "ustupa se", "može ustupiti" + sinonimi
    ASSIGNMENT_PATTERNS = [
        # Pattern: Subject + ustupa + object + recipient
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>ustupa|cedira|prepušta)\s+(?P<object>[^,.;!?]+?)\s+(?:na\s+)?(?P<recipient>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Subject + može ustupiti + object
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>može\s+ustupiti|može\s+cedirati|ovlašćen\s+je\s+da\s+ustupi)\s+(?P<object>[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Ustupanje + object + zahteva saglasnost
        r'(?P<modality>Ustupanje|Cesija|Prepuštanje)\s+(?P<object>[^,.;!?]+?)\s+(?:zahteva|podleže|uslovljeno\s+je)\s+(?P<condition>saglasn(?:ošću|osti)[^,.;!?]+?)[,.;!?]',
        
        # Pattern: Ustupanje je zabranjeno
        r'(?P<modality>Ustupanje|Cesija|Prepuštanje)\s+(?P<object>[^,.;!?]+?)\s+je\s+(?P<restriction>zabranjeno|ograničeno|isključeno|nedopušteno)[,.;!?]',
        
        # Pattern: Subject ustupa pravo na + object
        r'(?P<subject>[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[a-zšđčćž]+)*)\s+(?P<modality>ustupa\s+pravo|cedira\s+pravo)\s+na\s+(?P<object>[^,.;!?]+?)[,.;!?]',
    ]
    
    # Vague terms for ambiguity detection
    VAGUE_TERMS = [
        'odgovarajući', 'primeren', 'razuman', 'potreban', 'dovoljan',
        'adekvatan', 'prikladan', 'umeren', 'značajan', 'bitan',
        'relevantan', 'pogodan', 'prihvatljiv', 'zadovoljavajući'
    ]
    
    def __init__(self):
        """Initialize the normative extractor."""
        # Compile patterns for better performance
        self.obligation_patterns = [re.compile(p, re.IGNORECASE) for p in self.OBLIGATION_PATTERNS]
        self.prohibition_patterns = [re.compile(p, re.IGNORECASE) for p in self.PROHIBITION_PATTERNS]
        self.permission_patterns = [re.compile(p, re.IGNORECASE) for p in self.PERMISSION_PATTERNS]
        self.definition_patterns = [re.compile(p, re.IGNORECASE) for p in self.DEFINITION_PATTERNS]
        self.waiver_patterns = [re.compile(p, re.IGNORECASE) for p in self.WAIVER_PATTERNS]
        self.transfer_patterns = [re.compile(p, re.IGNORECASE) for p in self.TRANSFER_PATTERNS]
        self.assignment_patterns = [re.compile(p, re.IGNORECASE) for p in self.ASSIGNMENT_PATTERNS]
    
    def extract_obligations(self, text: str) -> List[Obligation]:
        """
        Extract obligations from text.
        
        Args:
            text: Input text
            
        Returns:
            List of Obligation objects
        """
        obligations = []
        
        for pattern in self.obligation_patterns:
            for match in pattern.finditer(text):
                groups = match.groupdict()
                
                # Extract temporal information if present
                temporal = None
                if groups.get('temporal'):
                    temporal = {'deadline': groups['temporal']}
                
                obligation = Obligation(
                    subject=groups.get('subject', 'Unknown').strip(),
                    action=groups.get('action', '').strip(),
                    object=groups.get('object', '').strip() if groups.get('object') else None,
                    modality=groups.get('modality', '').strip(),
                    condition=None,
                    temporal=temporal,
                    source_text=match.group(0),
                    confidence=0.8
                )
                obligations.append(obligation)
        
        return obligations
    
    def extract_prohibitions(self, text: str) -> List[Prohibition]:
        """
        Extract prohibitions from text.
        
        Args:
            text: Input text
            
        Returns:
            List of Prohibition objects
        """
        prohibitions = []
        
        for pattern in self.prohibition_patterns:
            for match in pattern.finditer(text):
                groups = match.groupdict()
                
                prohibition = Prohibition(
                    subject=groups.get('subject', 'Unknown').strip(),
                    action=groups.get('action', '').strip(),
                    object=groups.get('object', '').strip() if groups.get('object') else None,
                    modality=groups.get('modality', '').strip(),
                    exception=None,
                    source_text=match.group(0),
                    confidence=0.8
                )
                prohibitions.append(prohibition)
        
        return prohibitions
    
    def extract_permissions(self, text: str) -> List[Permission]:
        """
        Extract permissions from text.
        
        Args:
            text: Input text
            
        Returns:
            List of Permission objects
        """
        permissions = []
        
        for pattern in self.permission_patterns:
            for match in pattern.finditer(text):
                groups = match.groupdict()
                
                # Handle both 'object' and 'object2' (for "ima pravo na X" pattern)
                obj = groups.get('object') or groups.get('object2')
                
                permission = Permission(
                    subject=groups.get('subject', 'Unknown').strip(),
                    action=groups.get('action', '').strip() if groups.get('action') else 'ima pravo',
                    object=obj.strip() if obj else None,
                    modality=groups.get('modality', '').strip(),
                    condition=groups.get('condition', '').strip() if groups.get('condition') else None,
                    source_text=match.group(0),
                    confidence=0.8
                )
                permissions.append(permission)
        
        return permissions
    
    def extract_definitions(self, text: str) -> List[Definition]:
        """
        Extract definitions from text.
        
        Args:
            text: Input text
            
        Returns:
            List of Definition objects
        """
        definitions = []
        
        for pattern in self.definition_patterns:
            for match in pattern.finditer(text):
                groups = match.groupdict()
                
                definition = Definition(
                    term=groups.get('term', '').strip(),
                    definition=groups.get('definition', '').strip(),
                    scope=groups.get('scope', '').strip() if groups.get('scope') else None,
                    source_text=match.group(0),
                    confidence=0.8
                )
                definitions.append(definition)
        
        return definitions
    
    def extract_waivers(self, text: str) -> List[Waiver]:
        """
        Extract waivers from text.
        
        Args:
            text: Input text
            
        Returns:
            List of Waiver objects
        """
        waivers = []
        
        for pattern in self.waiver_patterns:
            for match in pattern.finditer(text):
                groups = match.groupdict()
                
                # Determine if waiver is valid (waivable)
                modality = groups.get('modality', '')
                waivable = 'ne može' not in modality.lower() and 'ništavo' not in groups.get('validity', '').lower()
                
                waiver = Waiver(
                    subject=groups.get('subject', 'Unknown').strip(),
                    right=groups.get('object', '').strip(),
                    waivable=waivable,
                    condition=None,
                    source_text=match.group(0),
                    confidence=0.75
                )
                waivers.append(waiver)
        
        return waivers
    
    def extract_transfers(self, text: str) -> List[Transfer]:
        """
        Extract transfers from text.
        
        Args:
            text: Input text
            
        Returns:
            List of Transfer objects
        """
        transfers = []
        
        for pattern in self.transfer_patterns:
            for match in pattern.finditer(text):
                groups = match.groupdict()
                
                transfer = Transfer(
                    from_party=groups.get('subject', 'Unknown').strip(),
                    to_party=groups.get('recipient', 'Unknown').strip() if groups.get('recipient') else 'Unknown',
                    subject=groups.get('object', '').strip(),
                    transferable='Ne može' not in groups.get('modality', ''),
                    condition=None,
                    source_text=match.group(0),
                    confidence=0.75
                )
                transfers.append(transfer)
        
        return transfers
    
    def extract_assignments(self, text: str) -> List[Assignment]:
        """
        Extract assignments from text.
        
        Args:
            text: Input text
            
        Returns:
            List of Assignment objects
        """
        assignments = []
        
        for pattern in self.assignment_patterns:
            for match in pattern.finditer(text):
                groups = match.groupdict()
                
                # Determine if consent is required
                requires_consent = 'saglasnost' in groups.get('condition', '').lower()
                
                assignment = Assignment(
                    assignor=groups.get('subject', 'Unknown').strip(),
                    assignee=groups.get('recipient', '').strip() if groups.get('recipient') else None,
                    subject=groups.get('object', '').strip(),
                    requires_consent=requires_consent,
                    condition=groups.get('condition', '').strip() if groups.get('condition') else None,
                    source_text=match.group(0),
                    confidence=0.75
                )
                assignments.append(assignment)
        
        return assignments
    
    def detect_ambiguity(self, text: str) -> List[AmbiguityScore]:
        """
        Detect ambiguous statements in text.
        
        Args:
            text: Input text
            
        Returns:
            List of AmbiguityScore objects
        """
        ambiguity_scores = []
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Count vague terms in sentence
            vague_count = 0
            vague_terms_found = []
            
            for term in self.VAGUE_TERMS:
                pattern = r'\b' + re.escape(term) + r'\b'
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                if matches:
                    vague_count += len(matches)
                    vague_terms_found.extend(matches)
            
            # Calculate ambiguity score (0.0 to 1.0)
            if vague_count > 0:
                # Score based on density of vague terms
                word_count = len(sentence.split())
                score = min(1.0, vague_count / max(1, word_count / 10))
                
                ambiguity_score = AmbiguityScore(
                    statement_type='general',
                    statement_id=f'stmt_{len(ambiguity_scores)}',
                    ambiguity_score=round(score, 2),
                    ambiguous_terms=vague_terms_found,
                    source_text=sentence
                )
                ambiguity_scores.append(ambiguity_score)
        
        return ambiguity_scores
    
    def detect_circular_definitions(self, definitions: List[Definition]) -> List[CircularDefinition]:
        """
        Detect circular definitions.
        
        Args:
            definitions: List of Definition objects
            
        Returns:
            List of CircularDefinition objects
        """
        circular_definitions = []
        
        # Build a map of term -> definition text
        term_map = {d.term.lower(): d.definition.lower() for d in definitions}
        
        # Check each definition for references to other terms
        for definition in definitions:
            term_lower = definition.term.lower()
            def_lower = definition.definition.lower()
            
            # Check if this term's definition references other terms
            referenced_terms = []
            for other_term in term_map.keys():
                if other_term != term_lower and other_term in def_lower:
                    referenced_terms.append(other_term)
            
            # Check for circular references
            for ref_term in referenced_terms:
                ref_definition = term_map.get(ref_term, '')
                
                # Direct circular reference: A -> B and B -> A
                if term_lower in ref_definition:
                    circular_def = CircularDefinition(
                        term1=definition.term,
                        term2=ref_term,
                        definition1=definition.definition,
                        definition2=term_map.get(ref_term, ''),
                        source_text=f"{definition.source_text} | {ref_term}: {term_map.get(ref_term, '')}",
                        confidence=0.8
                    )
                    circular_definitions.append(circular_def)
                
                # Indirect circular reference: A -> B -> C -> A
                else:
                    # Check second-level references
                    for second_term in term_map.keys():
                        if second_term != ref_term and second_term in ref_definition:
                            second_definition = term_map.get(second_term, '')
                            if term_lower in second_definition:
                                circular_def = CircularDefinition(
                                    term1=definition.term,
                                    term2=second_term,
                                    definition1=definition.definition,
                                    definition2=term_map.get(second_term, ''),
                                    source_text=f"{definition.source_text} | {ref_term} | {second_term}",
                                    confidence=0.7
                                )
                                circular_definitions.append(circular_def)
        
        # Remove duplicates (same circular reference detected from different starting points)
        unique_circulars = []
        seen_chains = set()
        for circ in circular_definitions:
            # Normalize chain to detect duplicates
            chain_key = tuple(sorted(circ.chain))
            if chain_key not in seen_chains:
                seen_chains.add(chain_key)
                unique_circulars.append(circ)
        
        return unique_circulars
    
    def extract(self, text: str) -> ExtractionResult:
        """
        Extract all normative content from text.
        
        Args:
            text: Input text
            
        Returns:
            ExtractionResult with all extracted normative content
        """
        start_time = time.time()
        
        # Extract all types
        obligations = self.extract_obligations(text)
        prohibitions = self.extract_prohibitions(text)
        permissions = self.extract_permissions(text)
        definitions = self.extract_definitions(text)
        waivers = self.extract_waivers(text)
        transfers = self.extract_transfers(text)
        assignments = self.extract_assignments(text)
        ambiguity_scores = self.detect_ambiguity(text)
        circular_definitions = self.detect_circular_definitions(definitions)
        
        # Build normative content
        normative_content = NormativeContent(
            obligations=obligations,
            prohibitions=prohibitions,
            permissions=permissions,
            definitions=definitions,
            waivers=waivers,
            transfers=transfers,
            assignments=assignments,
            ambiguity_scores=ambiguity_scores,
            circular_definitions=circular_definitions
        )
        
        processing_time = time.time() - start_time
        
        return ExtractionResult(
            normative_content=normative_content,
            processing_time=processing_time,
            text_length=len(text)
        )


# Singleton instance
_extractor = None

def get_extractor() -> NormativeExtractor:
    """Get singleton extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = NormativeExtractor()
    return _extractor


def extract_normative_content(text: str) -> Dict[str, Any]:
    """
    Extract normative content from text.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with extracted normative content
    """
    extractor = get_extractor()
    result = extractor.extract(text)
    return result.to_dict()

# Made with Bob
