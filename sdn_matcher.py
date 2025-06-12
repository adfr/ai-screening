#!/usr/bin/env python3
"""
SDN Watchlist Matcher
A two-step matching system for the OFAC SDN (Specially Designated Nationals) list.
Step 1: Keyword and citizenship matching for initial filtering
Step 2: LLM-based ranking for plausibility scoring
"""

import csv
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from difflib import SequenceMatcher
import json


class SDNMatcher:
    def __init__(self, sdn_file_path: str):
        self.sdn_file_path = sdn_file_path
        self.entries = []
        self.load_sdn_data()
    
    def load_sdn_data(self):
        """Load and parse the SDN CSV file."""
        with open(self.sdn_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 12:
                    entry = {
                        'id': row[0],
                        'name': row[1].strip('"'),
                        'type': row[2].strip() if row[2] != '-0-' else '',
                        'program': row[3].strip('"') if row[3] != '-0-' else '',
                        'title': row[4].strip('"') if row[4] != '-0-' else '',
                        'field5': row[5].strip() if row[5] != '-0-' else '',
                        'field6': row[6].strip() if row[6] != '-0-' else '',
                        'field7': row[7].strip() if row[7] != '-0-' else '',
                        'field8': row[8].strip() if row[8] != '-0-' else '',
                        'field9': row[9].strip() if row[9] != '-0-' else '',
                        'field10': row[10].strip() if row[10] != '-0-' else '',
                        'remarks': row[11].strip('"') if row[11] != '-0-' else '',
                    }
                    
                    # Parse additional info from remarks
                    remarks = entry['remarks']
                    entry['dob'] = self._extract_dob(remarks)
                    entry['nationality'] = self._extract_nationality(remarks)
                    entry['pob'] = self._extract_pob(remarks)
                    entry['aliases'] = self._extract_aliases(remarks)
                    
                    self.entries.append(entry)
    
    def _extract_dob(self, remarks: str) -> Optional[str]:
        """Extract date of birth from remarks."""
        dob_match = re.search(r'DOB\s+([^;]+)', remarks)
        if dob_match:
            return dob_match.group(1).strip()
        return None
    
    def _extract_nationality(self, remarks: str) -> Optional[str]:
        """Extract nationality from remarks."""
        nat_match = re.search(r'nationality\s+([^;]+)', remarks, re.IGNORECASE)
        if nat_match:
            return nat_match.group(1).strip()
        return None
    
    def _extract_pob(self, remarks: str) -> Optional[str]:
        """Extract place of birth from remarks."""
        pob_match = re.search(r'POB\s+([^;]+)', remarks)
        if pob_match:
            return pob_match.group(1).strip()
        return None
    
    def _extract_aliases(self, remarks: str) -> List[str]:
        """Extract aliases from remarks."""
        aliases = []
        aka_matches = re.findall(r"a\.k\.a\.\s+'([^']+)'", remarks)
        aliases.extend(aka_matches)
        alt_matches = re.findall(r"alt\.\s+([^;]+)", remarks)
        aliases.extend(alt_matches)
        return aliases
    
    def _fuzzy_match_score(self, str1: str, str2: str) -> float:
        """Calculate fuzzy match score between two strings."""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _parse_input(self, query: str) -> Dict[str, str]:
        """Parse user input to extract name, DOB, and nationality."""
        parts = [p.strip() for p in query.split(',')]
        
        result = {
            'name': parts[0] if parts else '',
            'dob': None,
            'nationality': None
        }
        
        # Try to identify DOB and nationality from remaining parts
        for part in parts[1:]:
            # Check if it's a date (various formats)
            if re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', part):
                result['dob'] = part
            # Check if it looks like a nationality/country
            elif len(part) < 20 and not any(char.isdigit() for char in part):
                result['nationality'] = part
        
        return result
    
    def _generate_name_variations(self, name: str) -> List[str]:
        """Generate name variations for flexible matching."""
        variations = [name.lower().strip()]
        
        # Split name into parts
        parts = name.lower().split()
        
        # Add variations with different orders
        if len(parts) >= 2:
            # Last name, first name
            variations.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
            # First + last only
            variations.append(f"{parts[0]} {parts[-1]}")
        
        # Remove common prefixes/suffixes
        cleaned_parts = []
        for part in parts:
            # Remove common titles and suffixes
            if part not in ['mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'jr', 'sr', 'ii', 'iii']:
                cleaned_parts.append(part)
        
        if cleaned_parts and cleaned_parts != parts:
            variations.append(' '.join(cleaned_parts))
        
        # Add partial matches (useful for typos)
        for part in parts:
            if len(part) > 3:  # Only for longer names
                variations.append(part)
        
        return list(set(variations))  # Remove duplicates
    
    def _flexible_name_match(self, query_name: str, target_name: str, aliases: List[str]) -> Tuple[float, str]:
        """Perform flexible name matching with variations."""
        best_score = 0.0
        best_match_type = ""
        
        query_variations = self._generate_name_variations(query_name)
        target_variations = self._generate_name_variations(target_name)
        
        # Check main name
        for q_var in query_variations:
            for t_var in target_variations:
                score = self._fuzzy_match_score(q_var, t_var)
                if score > best_score:
                    best_score = score
                    best_match_type = "name"
        
        # Check aliases
        for alias in aliases:
            alias_variations = self._generate_name_variations(alias)
            for q_var in query_variations:
                for a_var in alias_variations:
                    score = self._fuzzy_match_score(q_var, a_var)
                    if score > best_score:
                        best_score = score
                        best_match_type = "alias"
        
        return best_score, best_match_type

    def step1_filter(self, query: str, threshold: float = 0.4) -> List[Dict]:
        """
        Step 1: Filter entries based on flexible name matching only.
        Returns list of potential matches with basic scoring.
        """
        parsed = self._parse_input(query)
        query_name = parsed['name'].lower()
        
        matches = []
        
        for entry in self.entries:
            # Flexible name matching
            name_score, match_type = self._flexible_name_match(
                query_name, entry['name'], entry['aliases']
            )
            
            if name_score > threshold:
                matches.append({
                    'entry': entry,
                    'score': name_score,
                    'match_reasons': [f"{match_type} match: {name_score:.2f}"]
                })
        
        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:100]  # Return top 100 matches for LLM processing
    
    def step2_llm_rank(self, query: str, filtered_matches: List[Dict]) -> List[Dict]:
        """
        Step 2: Use LLM to rank filtered matches by plausibility.
        Considers nationality, DOB, and other contextual factors.
        """
        parsed = self._parse_input(query)
        query_dob = parsed['dob']
        query_nationality = parsed['nationality']
        
        for match in filtered_matches:
            entry = match['entry']
            enhanced_score = match['score']
            additional_reasons = []
            
            # DOB matching (strong indicator)
            if query_dob and entry['dob']:
                if self._compare_dates(query_dob, entry['dob']):
                    enhanced_score += 0.3
                    additional_reasons.append("DOB match")
            
            # Nationality matching
            if query_nationality and entry['nationality']:
                nat_score = self._fuzzy_match_score(query_nationality, entry['nationality'])
                if nat_score > 0.8:
                    enhanced_score += 0.2
                    additional_reasons.append("Nationality match")
            
            # Country/Program matching (for organizations)
            if query_nationality and entry['program']:
                country_score = self._fuzzy_match_score(query_nationality, entry['program'])
                if country_score > 0.8:
                    enhanced_score += 0.15
                    additional_reasons.append("Country/Program match")
            
            # Type consistency (individual vs entity)
            if 'individual' in entry['type'].lower():
                if not any(org_word in parsed['name'].lower() 
                          for org_word in ['company', 'corp', 'inc', 'ltd', 'bank', 'association']):
                    enhanced_score += 0.05
                    additional_reasons.append("Individual type match")
            else:
                if any(org_word in parsed['name'].lower() 
                      for org_word in ['company', 'corp', 'inc', 'ltd', 'bank', 'association']):
                    enhanced_score += 0.05
                    additional_reasons.append("Entity type match")
            
            # Context relevance from remarks
            if entry['remarks']:
                remarks_lower = entry['remarks'].lower()
                query_words = parsed['name'].lower().split()
                context_matches = sum(1 for word in query_words if word in remarks_lower)
                if context_matches > 0:
                    enhanced_score += context_matches * 0.02
                    additional_reasons.append(f"Context relevance ({context_matches} terms)")
            
            match['match_reasons'].extend(additional_reasons)
            match['llm_score'] = min(enhanced_score, 1.0)  # Cap at 1.0
            match['confidence'] = self._calculate_confidence(match['llm_score'], additional_reasons)
        
        # Re-sort by LLM score
        filtered_matches.sort(key=lambda x: x['llm_score'], reverse=True)
        return filtered_matches
    
    def _compare_dates(self, query_date: str, entry_date: str) -> bool:
        """Compare dates allowing for different formats."""
        # Simple comparison - in production you'd want more robust date parsing
        query_clean = re.sub(r'[^0-9]', '', query_date)
        entry_clean = re.sub(r'[^0-9]', '', entry_date)
        
        # Check if dates contain similar numbers
        if len(query_clean) >= 6 and len(entry_clean) >= 6:
            return query_clean in entry_clean or entry_clean in query_clean
        
        return False
    
    def _calculate_confidence(self, score: float, additional_reasons: List[str]) -> str:
        """Calculate confidence level based on score and additional factors."""
        if score > 0.8 and len(additional_reasons) >= 2:
            return 'HIGH'
        elif score > 0.6 and len(additional_reasons) >= 1:
            return 'MEDIUM-HIGH'
        elif score > 0.5:
            return 'MEDIUM'
        elif score > 0.3:
            return 'LOW-MEDIUM'
        else:
            return 'LOW'
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Main search function that combines both steps.
        """
        # Step 1: Initial filtering
        filtered = self.step1_filter(query)
        
        if not filtered:
            return []
        
        # Step 2: LLM ranking
        ranked = self.step2_llm_rank(query, filtered)
        
        # Format results
        results = []
        for match in ranked[:max_results]:
            entry = match['entry']
            result = {
                'name': entry['name'],
                'type': entry['type'],
                'score': match['llm_score'],
                'confidence': match['confidence'],
                'match_reasons': match['match_reasons'],
                'details': {
                    'id': entry['id'],
                    'program': entry['program'],
                    'nationality': entry['nationality'],
                    'dob': entry['dob'],
                    'pob': entry['pob'],
                    'aliases': entry['aliases'],
                    'remarks': entry['remarks']
                }
            }
            results.append(result)
        
        return results


def main():
    """Example usage of the SDN matcher."""
    matcher = SDNMatcher('sdn.csv')
    
    # Test cases
    test_queries = [
        "john mccain",
        "john mcain, 21/06/1955, american",
        "abbas, palestine",
        "banco cuba",
        "al zawahiri, 1951, egypt"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Searching for: {query}")
        print('='*60)
        
        results = matcher.search(query, max_results=5)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['name']} ({result['type']})")
                print(f"   Score: {result['score']:.2f} - Confidence: {result['confidence']}")
                print(f"   Reasons: {', '.join(result['match_reasons'])}")
                if result['details']['nationality']:
                    print(f"   Nationality: {result['details']['nationality']}")
                if result['details']['dob']:
                    print(f"   DOB: {result['details']['dob']}")
                if result['details']['aliases']:
                    print(f"   Aliases: {', '.join(result['details']['aliases'][:3])}")
        else:
            print("No matches found.")


if __name__ == "__main__":
    main()