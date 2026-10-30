import regex
NEW=regex.compile(r"(?<![\p{L}\p{N}])(?:(?:go|last|survive|live)\s+without\s+(?:food|water|eating|drinking)|survive\s+(?:in|at)\s+[^?.!]{0,25}?(?:-?\d+(?:[.,]\d+)?\s*°?\s*[cf]\b|cold|icy|freezing)|\d+\s*ppm|(?:co|carbon monoxide)\s+(?:reading|level|alarm|detector)s?)(?![\p{L}])",regex.I|regex.V1)
