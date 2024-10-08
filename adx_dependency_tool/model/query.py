import re
from ..kusto_cleaner import clean


class Query():
    def __init__(self, query_id, content, function_names, table_names):
        self.query_id = query_id
        self.content = clean(content)
        self.function_names = function_names
        self.table_names = table_names
        self.resolved_functions, self.resolved_tables = self._resolve_conflict_functions_and_tables()
        self.used_functions = self._get_used_functions()
        self.used_tables = self._get_used_tables()

    def _get_used_functions(self):
        pattern = r'(?<!-)\b(\w+)\s*(?=\(|\s)'
        used_functions = re.findall(pattern, self.content)
        used_functions = [
            f for f in used_functions if f in self.function_names and f not in self.resolved_tables]
        return list(set(used_functions))

    def _get_used_tables(self):
        pattern = r"(?:table\(['\"](\w+)['\"]\))|(?<!-)\b(\w+)\b"
        used_tables = re.findall(pattern, self.content)
        used_tables = [x for t in used_tables for x in t]
        used_tables = [
            t for t in used_tables if t in self.table_names and t not in self.resolved_functions]
        return list(set(used_tables))

    def _get_conflict_functions_and_tables(self):
        return list(set(self.function_names) & set(self.table_names))

    def _resolve_conflict_functions_and_tables(self):
        conflict_functions_and_tables = self._get_conflict_functions_and_tables()
        resolved_functions = []
        resolved_tables = []
        for cft in conflict_functions_and_tables:
            pattern = rf"table\(['\"]{re.escape(cft)}['\"]\)"
            match = re.search(pattern, self.content)
            if match:
                resolved_tables.append(cft)
            else:
                resolved_functions.append(cft)
        return resolved_functions, resolved_tables
