import numpy as np
import os

class LUTParser:
    """
    Parser for .cube LUT files with comprehensive metadata extraction
    """
    def __init__(self, cube_path):
        self.cube_path = cube_path
        self.title = ""
        self.size = 0
        self.domain_min = None
        self.domain_max = None
        self.data = None
        self.metadata = {}
        self._parse_cube_file()
    
    def _parse_cube_file(self):
        """Parse .cube LUT file and extract data and metadata"""
        with open(self.cube_path, 'r') as f:
            lines = f.readlines()
        
        # Parse header for metadata
        self.metadata = {
            'filename': os.path.basename(self.cube_path),
            'filesize': os.path.getsize(self.cube_path),
            'comments': []
        }
        
        data_start_line = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                if line.startswith('#'):
                    self.metadata['comments'].append(line[1:].strip())
                continue
                
            if line.startswith('TITLE'):
                parts = line.split('"')
                if len(parts) >= 3:
                    self.title = parts[1]
                    self.metadata['title'] = self.title
                else:
                    self.title = line.split(' ', 1)[1].strip('"')
                    self.metadata['title'] = self.title
            elif line.startswith('LUT_3D_SIZE'):
                self.size = int(line.split()[-1])
                self.metadata['size'] = self.size
            elif line.startswith('DOMAIN_MIN'):
                self.domain_min = list(map(float, line.split()[1:]))
                self.metadata['domain_min'] = self.domain_min
            elif line.startswith('DOMAIN_MAX'):
                self.domain_max = list(map(float, line.split()[1:]))
                self.metadata['domain_max'] = self.domain_max
            elif all(c.isdigit() or c == '.' or c == '-' or c.isspace() for c in line):
                # This looks like the start of the data section
                data_start_line = i
                break
        
        # If domain not specified, use default 0-1
        if self.domain_min is None:
            self.domain_min = [0.0, 0.0, 0.0]
        if self.domain_max is None:
            self.domain_max = [1.0, 1.0, 1.0]
        
        # Parse LUT data
        data_lines = [line.strip() for line in lines[data_start_line:] 
                     if line.strip() and not line.startswith(('#', 'TITLE', 'LUT_3D_SIZE', 'DOMAIN_MIN', 'DOMAIN_MAX'))]
        
        try:
            self.data = np.array([list(map(float, line.split())) for line in data_lines])
            
            # Basic validation
            expected_entries = self.size ** 3
            if len(self.data) != expected_entries:
                print(f"Warning: LUT data size mismatch. Expected {expected_entries}, got {len(self.data)}")
        except Exception as e:
            print(f"Error parsing LUT data: {e}")
            raise
    
    def infer_color_spaces(self):
        """
        Attempt to infer source and target color spaces based on LUT characteristics
        This is a heuristic approach and may not be accurate for all LUTs
        """
        # Analyze LUT characteristics
        min_values = np.min(self.data, axis=0)
        max_values = np.max(self.data, axis=0)
        mean_values = np.mean(self.data, axis=0)
        std_values = np.std(self.data, axis=0)
        
        # Store values in metadata
        self.metadata['min_values'] = min_values
        self.metadata['max_values'] = max_values
        self.metadata['mean_values'] = mean_values
        self.metadata['std_values'] = std_values
        
        # Infer source color space based on filename and metadata
        filename = self.metadata['filename'].lower()
        
        # Default assumptions
        source_space = "Unknown"
        target_space = "Unknown"
        
        # Check for common indicators in filename or title
        if 'slog3' in filename or 'sl3' in filename or 's-log3' in filename:
            source_space = "S-Log3/S-Gamut3"
        elif 'logc' in filename or 'log-c' in filename:
            source_space = "ARRI LogC/AWG"
        elif 'redlog' in filename or 'red-log' in filename:
            source_space = "RED Log3G10/REDWideGamut"
        elif 'v-log' in filename or 'vlog' in filename:
            source_space = "V-Log/V-Gamut"
        elif 'log2' in filename:
            source_space = "Cineon Log/Film"
        
        # Check for target space indicators
        if 'rec709' in filename or '709' in filename:
            target_space = "Rec.709"
        elif 'rec2020' in filename or '2020' in filename:
            target_space = "Rec.2020"
        elif 'p3' in filename or 'dci' in filename:
            target_space = "P3-D65"
        
        # For V2_Sl3Sg3 files, we can be more specific
        if 'sl3sg3' in filename.lower():
            source_space = "S-Log3/S-Gamut3"
            if 'b&w' in filename.lower():
                target_space = "Rec.709 (B&W)"
        
        # Check title for additional clues
        if self.title:
            title = self.title.lower()
            if 'rec709' in title or '709' in title:
                target_space = "Rec.709"
            elif source_space == "Unknown" and ('slog' in title or 's-log' in title):
                source_space = "S-Log3/S-Gamut3"
        
        # Look for gamma indicators
        gamma = "Unknown"
        if 'g2.4' in filename or 'gamma2.4' in filename or '2.4' in filename:
            gamma = "2.4"
        elif 'g2.2' in filename or 'gamma2.2' in filename or '2.2' in filename:
            gamma = "2.2"
        
        # For artistic LUTs (film emulation, etc.), assume Rec.709 output
        if any(term in filename.lower() for term in ['film', 'cinema', 'movie', 'vintage', 'retro']):
            target_space = "Rec.709 (Stylized)"
        
        # Store inferred spaces
        self.metadata['inferred_source_space'] = source_space
        self.metadata['inferred_target_space'] = target_space
        self.metadata['inferred_gamma'] = gamma
        
        return {
            'source_space': source_space,
            'target_space': target_space,
            'gamma': gamma
        }
    
    def get_data(self):
        """Return parsed LUT data"""
        return self.data
    
    def get_metadata(self):
        """Return all LUT metadata"""
        return self.metadata 