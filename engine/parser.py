# engine/parser.py
import os

class CsvParser:
    """
    A custom CSV parser that reads and parses CSV files from scratch.
    It now also infers data types.
    """
    def __init__(self, filepath, separator=','):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        self.filepath = filepath
        self.separator = separator
        self.header = self._get_header()
        # --- NEW: Infer and store types ---
        self.column_types = self._infer_types()

    def _clean_line(self, line):
        """Helper to strip whitespace and newline characters."""
        return line.strip()

    def _get_header(self):
        """
        Reads only the first line of the file to get the headers.
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                header_line = self._clean_line(f.readline())
            # Strip spaces from headers
            return [h.strip() for h in header_line.split(self.separator)]
        except Exception as e:
            print(f"Error reading header: {e}")
            return []

    def get_header(self):
        """Public method to access the parsed header."""
        return self.header

    # --- NEW: Public method to get types ---
    def get_column_types(self):
        """Public method to access the inferred column types."""
        return self.column_types

    def _is_int(self, val):
        try:
            int(val)
            return True
        except ValueError:
            return False

    def _is_float(self, val):
        try:
            float(val)
            return True
        except ValueError:
            return False

    # --- NEW: Type inference logic ---
    def _infer_types(self):
        """
        Infers column types (int, float, str) by sampling the first 50 rows.
        """
        types = {col: 'int' for col in self.header} # Start by assuming all are int
        
        sample_count = 0
        for row in self.parse(): # This uses the parse generator
            if sample_count >= 50:
                break
            
            for col_name, value in row.items():
                if value is None or value == '':
                    continue # Skip empty values
                
                current_type = types[col_name]
                
                # If it's already a string, it stays a string
                if current_type == 'str':
                    continue
                
                # Check if it's an int
                if current_type == 'int':
                    if not self._is_int(value):
                        # Not an int, check if it's a float
                        types[col_name] = 'float'
                
                # Check if it's a float (or was just downgraded from int)
                if types[col_name] == 'float':
                    if not self._is_float(value):
                        # Not a float, downgrade to string
                        types[col_name] = 'str'
                        
            sample_count += 1
            
        print(f"Inferred types for {self.filepath}: {types}")
        return types

    def parse(self):
        """
        A generator function that reads the CSV file line-by-line.
        It yields each row as a dictionary, mapping headers to values.
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                # Skip the header line which we've already processed
                f.readline()
                
                line_number = 1
                line = f.readline()
                while line:
                    line_number += 1
                    cleaned_line = self._clean_line(line)
                    if cleaned_line:  # Skip empty lines
                        # Strip spaces from values
                        values = [v.strip() for v in cleaned_line.split(self.separator)]
                        
                        # Handle validation for consistent column counts
                        if len(values) == len(self.header):
                            # Creates the dictionary-like format
                            row_dict = dict(zip(self.header, values))
                            yield row_dict
                        else:
                            print(f"Warning: Skipping malformed line {line_number}. Expected {len(self.header)} columns, got {len(values)}: {line}")
                    
                    line = f.readline()
        except Exception as e:
            print(f"Error during parsing: {e}")
            return