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
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 12:
                    entry_dict = {
                        'id': row[0],
                        'name': row[1].strip('"'),
                        'type': row[2].strip() if row[2] != '-0-' else '',
                        'program': row[3].strip('"') if row[3] != '-0-' else '',
                        'title': row[4].strip('"') if row[4] != '-0-' else '',
                        'remarks': row[11].strip('"') if row[11] != '-0-' else '',
                    }
                    
                    # Parse additional info from remarks
                    remarks = entry_dict['remarks']
                    entry_dict['dob'] = self._extract_dob(remarks)
                    entry_dict['nationality'] = self._extract_nationality(remarks)
                    entry_dict['pob'] = self._extract_pob(remarks)
                    entry_dict['aliases'] = self._extract_aliases(remarks)
                    
                    entries.append(SDNEntry(**entry_dict))
        
        return entries
    
    @staticmethod
    def _extract_dob(remarks: str) -> Optional[str]:
        """Extract date of birth from remarks."""
        dob_match = re.search(r'DOB\s+([^;]+)', remarks)
        if dob_match:
            return dob_match.group(1).strip()
        return None
    
    @staticmethod
    def _extract_nationality(remarks: str) -> Optional[str]:
        """Extract nationality from remarks."""
        nat_match = re.search(r'nationality\s+([^;]+)', remarks, re.IGNORECASE)
        if nat_match:
            return nat_match.group(1).strip()
        return None
    
    @staticmethod
    def _extract_pob(remarks: str) -> Optional[str]:
        """Extract place of birth from remarks."""
        pob_match = re.search(r'POB\s+([^;]+)', remarks)
        if pob_match:
            return pob_match.group(1).strip()
        return None
    
    @staticmethod
    def _extract_aliases(remarks: str) -> List[str]:
        """Extract aliases from remarks."""
        aliases = []
        aka_matches = re.findall(r"a\.k\.a\.\s+'([^']+)'", remarks)
        aliases.extend(aka_matches)
        alt_matches = re.findall(r"alt\.\s+([^;]+)", remarks)
        aliases.extend(alt_matches)
        return aliases