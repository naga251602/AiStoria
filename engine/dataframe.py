# engine/dataframe.py
from .parser import CsvParser
import types

class DataFrame:
    """
    A custom DataFrame structure that can be sourced from a file (via CsvParser)
    or from an in-memory list of dicts (e.g., from a join).
    """
    def __init__(self, source):
        self.source_type = 'list'
        self.data = []
        self.header = []
        self.parser = None
        self.filepath = None
        self.column_types = {}

        if isinstance(source, str): # Source is a filepath
            self.source_type = 'file'
            self.parser = CsvParser(source)
            self.header = self.parser.get_header()
            self.filepath = source
            # Get types from the parser
            self.column_types = self.parser.get_column_types()
            
        elif isinstance(source, list): # Source is in-memory data
            self.source_type = 'list'
            self.data = source
            if self.data:
                self.header = list(self.data[0].keys())
            # Infer types from the list data
            self.column_types = self._infer_types_from_list(self.data)
        else:
            raise ValueError("DataFrame source must be a filepath (str) or data (list)")

    def get_header(self):
        """Returns the list of column headers."""
        return self.header

    @property
    def columns(self):
        """Alias for get_header() to support AI generated code like df.columns"""
        return self.header

    def get_column_types(self):
        """Public method to access the column types."""
        return self.column_types

    def _get_data(self):
        """
        Internal helper to get a fresh iterator of all data.
        """
        if self.source_type == 'file':
            return self.parser.parse()
        else: # 'list'
            return iter(self.data) # Return an iterator for consistency

    def __len__(self):
        """
        Allows len(df) to work.
        """
        if self.source_type == 'file':
            count = 0
            for _ in self.parser.parse(): # Use a fresh generator
                count += 1
            return count
        else: # 'list'
            return len(self.data)
            
    def _infer_types_from_list(self, data):
        """
        Infers types from an in-memory list of dicts (e.g., after a join).
        """
        if not data:
            return {}
            
        def _is_int(val):
            try:
                int(val)
                return True
            except (ValueError, TypeError):
                return False
        def _is_float(val):
            try:
                float(val)
                return True
            except (ValueError, TypeError):
                return False

        types = {col: 'int' for col in self.header}
        sample_count = 0
        for row in data:
            if sample_count >= 50: 
                break
            
            for col_name, value in row.items():
                if value is None or value == '':
                    continue 
                
                current_type = types.get(col_name, 'int')
                if current_type == 'str':
                    continue
                
                value_str = str(value)
                if current_type == 'int':
                    if not _is_int(value_str):
                        types[col_name] = 'float'
                
                if types[col_name] == 'float':
                    if not _is_float(value_str):
                        types[col_name] = 'str'
            sample_count += 1
        return types

    def filter(self, condition_func):
        """
        Implements the 'filter' (selection) operation.
        Returns a *new DataFrame* with the filtered data.
        """
        filtered_data = [row for row in self._get_data() if condition_func(row)]
        return DataFrame(source=filtered_data)

    def project(self, columns):
        """
        Implements the 'project' (column selection) operation.
        Returns a *list* of dicts (not a DataFrame).
        """
        projected_data = []
        for row in self._get_data():
            new_row = {col: row[col] for col in columns if col in row}
            projected_data.append(new_row)
        return projected_data

    def groupby(self, column_name):
        """
        Implements the 'group-by' operation.
        Returns a dictionary where keys are group values
        and values are lists of rows.
        """
        groups = {}
        for row in self._get_data():
            key = row.get(column_name)
            if key is not None:
                if key not in groups:
                    groups[key] = []
                groups[key].append(row)
        return groups

    def aggregate(self, groups, agg_func_map):
        """
        Implements the 'aggregation' operation.
        Takes the output of groupby() and an aggregation map.
        Returns a dictionary (not a DataFrame).
        Supported functions: count, sum, avg, min, max.
        """
        results = {}
        for key, rows in groups.items():
            agg_result = {}
            for col, func in agg_func_map.items():
                
                if func == 'count':
                    agg_result[col] = len(rows)
                
                elif func == 'sum':
                    total = 0
                    for row in rows:
                        try:
                            total += float(row[col])
                        except (ValueError, TypeError):
                            continue
                    agg_result[col] = total
                
                elif func == 'avg':
                    total = 0
                    count = 0
                    for row in rows:
                        try:
                            total += float(row[col])
                            count += 1
                        except (ValueError, TypeError):
                            continue
                    agg_result[col] = total / count if count > 0 else 0

                # --- MIN Operation ---
                elif func == 'min':
                    min_val = None
                    for row in rows:
                        try:
                            val = float(row[col])
                            if min_val is None or val < min_val:
                                min_val = val
                        except (ValueError, TypeError):
                            continue
                    agg_result[col] = min_val

                # --- MAX Operation ---
                elif func == 'max':
                    max_val = None
                    for row in rows:
                        try:
                            val = float(row[col])
                            if max_val is None or val > max_val:
                                max_val = val
                        except (ValueError, TypeError):
                            continue
                    agg_result[col] = max_val
            
            results[key] = agg_result
        return results

    def join(self, right_dataframe, left_on, right_on):
        """
        Implements an 'inner join' operation.
        Returns a *new DataFrame* with the joined data.
        """
        joined_data = []
        
        # Build the hash table (dictionary) from the right table
        right_rows_by_key = {}
        for right_row in right_dataframe._get_data():
            key = right_row.get(right_on)
            if key not in right_rows_by_key:
                right_rows_by_key[key] = []
            right_rows_by_key[key].append(right_row)

        # Now stream the left table and perform the join
        for left_row in self._get_data():
            left_key = left_row.get(left_on)
            if left_key in right_rows_by_key:
                for right_row in right_rows_by_key[left_key]:
                    new_row = left_row.copy()
                    for key, value in right_row.items():
                        if key == right_on: 
                            continue
                        if key not in new_row:
                            new_row[key] = value
                        else:
                            filepath_tag = right_dataframe.filepath if right_dataframe.filepath else 'joined'
                            new_row[f"{filepath_tag}.{key}"] = value
                    joined_data.append(new_row)
                    
        return DataFrame(source=joined_data)