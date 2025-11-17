# engine/parser.py
import os

class CsvParser:
    """
    A custom CSV parser that reads and parses CSV files from scratch.
    Designed to scale to very large CSV files (GB+).
    
    Features:
      - Streaming, line-by-line parsing (no full file load into memory)
      - Optional type inference from a sample of rows
      - Optional casting of values to inferred types
      - Optional chunked iteration for batch processing
    """
    def __init__(self, filepath, separator=',', infer_types=True, sample_size=50):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        self.filepath = filepath
        self.separator = separator
        self.header = self._get_header()

        if infer_types:
            self.column_types = self._infer_types(sample_size=sample_size)
        else:
            # Default everything to str if you do not want to infer
            self.column_types = {col: 'str' for col in self.header}

    # ---------- Helpers ----------

    def _clean_line(self, line):
        """Strip whitespace and newline characters."""
        return line.strip()

    def _get_header(self):
        """Reads only the first line of the file to get the headers."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                header_line = self._clean_line(f.readline())
            return [h.strip() for h in header_line.split(self.separator)]
        except Exception as e:
            print(f"Error reading header: {e}")
            return []

    def get_header(self):
        return self.header

    def get_column_types(self):
        return self.column_types

    def _is_int(self, val: str) -> bool:
        try:
            int(val)
            return True
        except ValueError:
            return False

    def _is_float(self, val: str) -> bool:
        try:
            float(val)
            return True
        except ValueError:
            return False

    def _cast_value(self, col_name, value):
        """
        Casts a single string value into the inferred type.
        Empty strings become None.
        """
        if value == '':
            return None

        t = self.column_types.get(col_name, 'str')

        if t == 'int':
            try:
                return int(value)
            except ValueError:
                # Fallback if inference was wrong
                return value
        elif t == 'float':
            try:
                return float(value)
            except ValueError:
                return value
        else:
            return value

    # ---------- Type inference ----------

    def _infer_types(self, sample_size=50):
        """
        Infers column types (int, float, str) by scanning up to `sample_size` rows.
        Still fully streaming: it only reads what it needs.
        """
        types = {col: 'int' for col in self.header}  # optimistic start

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                # Skip header
                f.readline()

                sample_count = 0
                for line in f:
                    if sample_count >= sample_size:
                        break

                    cleaned_line = self._clean_line(line)
                    if not cleaned_line:
                        continue

                    values = [v.strip() for v in cleaned_line.split(self.separator)]
                    if len(values) != len(self.header):
                        # Skip malformed lines from inference
                        continue

                    row = dict(zip(self.header, values))

                    for col_name, value in row.items():
                        if value == '':
                            continue

                        current_type = types[col_name]

                        if current_type == 'str':
                            continue

                        # Check for int
                        if current_type == 'int':
                            if not self._is_int(value):
                                # downgrade to float candidate
                                types[col_name] = 'float'
                                current_type = 'float'

                        # Check for float
                        if current_type == 'float':
                            if not self._is_float(value):
                                # downgrade to string
                                types[col_name] = 'str'

                    sample_count += 1

        except Exception as e:
            print(f"Error during type inference: {e}")
            types = {col: 'str' for col in self.header}

        print(f"Inferred types for {self.filepath}: {types}")
        return types

    # ---------- Streaming parsers ----------

    def parse(self, cast=True):
        """
        Generator that yields one row at a time as a dict.

        Parameters
        ----------
        cast : bool
            If True, cast values to the inferred types.
            If False, leave everything as raw strings.
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                # Skip header
                f.readline()
                line_number = 1

                for line in f:
                    line_number += 1
                    cleaned_line = self._clean_line(line)
                    if not cleaned_line:
                        continue

                    values = [v.strip() for v in cleaned_line.split(self.separator)]

                    if len(values) != len(self.header):
                        print(
                            f"Warning: Skipping malformed line {line_number}. "
                            f"Expected {len(self.header)} columns, got {len(values)}: {line!r}"
                        )
                        continue

                    row_dict = dict(zip(self.header, values))

                    if cast:
                        for col in row_dict:
                            row_dict[col] = self._cast_value(col, row_dict[col])

                    yield row_dict
        except Exception as e:
            print(f"Error during parsing: {e}")
            return

    def parse_chunks(self, chunk_size=1000, cast=True):
        """
        Generator that yields lists of rows (chunks) of size `chunk_size`.

        Useful for massive datasets where you want to operate on batches.
        """
        batch = []
        for row in self.parse(cast=cast):
            batch.append(row)
            if len(batch) >= chunk_size:
                yield batch
                batch = []

        # Yield any remaining rows
        if batch:
            yield batch
