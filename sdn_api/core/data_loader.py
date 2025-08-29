import csv
import re
from typing import List, Optional
from pathlib import Path

from ..models.sdn import SDNEntry


class SDNDataLoader:
    """Handles loading and parsing of SDN CSV data."""
    
    def __init__(self, sdn_file_path: str):
        self.sdn_file_path = Path(sdn_file_path)
        if not self.sdn_file_path.exists():
            raise FileNotFoundError(f"SDN file not found: {sdn_file_path}")
    
    def load_entries(self) -> List[SDNEntry]:
        """Load and parse all SDN entries from CSV file."""
        entries = []
        
        with open(self.sdn_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # New CSV format: uid, name, details
                details = row.get('details', '')
                
                entry_dict = {
                    'id': row.get('uid', ''),
                    'name': row.get('name', ''),
                    'type': self._extract_type(details),
                    'program': self._extract_program(details),
                    'title': '',  # Not in new format
                    'remarks': details,  # Store full details as remarks
                }
                
                # Parse additional info from details
                entry_dict['dob'] = self._extract_dob(details)
                entry_dict['nationality'] = self._extract_nationality(details)
                entry_dict['pob'] = self._extract_pob(details)
                entry_dict['aliases'] = self._extract_aliases(details)
                
                entries.append(SDNEntry(**entry_dict))
        
        return entries
    
    @staticmethod
    def _extract_type(details: str) -> str:
        """Extract entity type from details."""
        type_match = re.search(r'Type:\s*([^|]+)', details)
        if type_match:
            return type_match.group(1).strip()
        return ''
    
    @staticmethod
    def _extract_program(details: str) -> str:
        """Extract sanctions program from details."""
        program_match = re.search(r'Programs?:\s*([^|]+)', details)
        if program_match:
            return program_match.group(1).strip()
        return ''
    
    @staticmethod
    def _extract_dob(remarks: str) -> Optional[str]:
        """Extract date of birth from remarks."""
        # Updated pattern for new format: "Birthdate: DD/MM/YYYY"
        dob_match = re.search(r'Birthdate:\s*([^|]+)', remarks)
        if dob_match:
            return dob_match.group(1).strip()
        return None
    
    @staticmethod
    def _extract_nationality(remarks: str) -> Optional[str]:
        """Extract nationality from remarks."""
        # Updated pattern for new format: "Nationality: Country"
        nat_match = re.search(r'Nationality:\s*([^|]+)', remarks, re.IGNORECASE)
        if nat_match:
            return nat_match.group(1).strip()
        return None
    
    @staticmethod
    def _extract_pob(remarks: str) -> Optional[str]:
        """Extract place of birth from remarks."""
        # Updated pattern for new format: "Place of Birth: Location"
        pob_match = re.search(r'Place of Birth:\s*([^|]+)', remarks)
        if pob_match:
            return pob_match.group(1).strip()
        return None
    
    @staticmethod
    def _extract_aliases(remarks: str) -> List[str]:
        """Extract aliases from remarks."""
        aliases = []
        # Updated pattern for new format: "Aliases: Name1; Name2; Name3"
        alias_match = re.search(r'Aliases:\s*([^|]+)', remarks, re.IGNORECASE)
        if alias_match:
            alias_str = alias_match.group(1).strip()
            # Split by semicolon for multiple aliases
            aliases = [a.strip() for a in alias_str.split(';') if a.strip()]
        return aliases