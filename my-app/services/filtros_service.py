from typing import Dict, List, Tuple, Optional


class FiltrosQueryBuilder:
    def __init__(self, table: str, alias: str = ''):
        self.table = table
        self.alias = alias
        self.joins: List[str] = []
        self.where: List[str] = []
        self.params: List[str] = []
        self.group_by: Optional[str] = None
        self.order_by: Optional[str] = None

    def add_join(self, sql: str):
        self.joins.append(sql)

    def add_where(self, column: str, operator: str, value: str):
        if value == '' or value is None:
            return
        if operator == 'LIKE':
            self.where.append(f"{column} LIKE %s")
            self.params.append(f"%{value}%")
        elif operator == 'DATE_GTE':
            self.where.append(f"DATE({column}) >= %s")
            self.params.append(value)
        elif operator == 'DATE_LTE':
            self.where.append(f"DATE({column}) <= %s")
            self.params.append(value)
        elif operator == 'EQUALS':
            self.where.append(f"{column} = %s")
            self.params.append(value)
        elif operator == 'BETWEEN':
            self.where.append(f"{column} BETWEEN %s AND %s")
            self.params.extend(value)

    def build_select(self, columns: str) -> str:
        sql = f"SELECT {columns} FROM {self.table}"
        if self.alias:
            sql = f"SELECT {columns} FROM {self.table} AS {self.alias}"
        for j in self.joins:
            sql += f" {j}"
        if self.where:
            sql += " WHERE " + " AND ".join(self.where)
        if self.group_by:
            sql += f" GROUP BY {self.group_by}"
        if self.order_by:
            sql += f" ORDER BY {self.order_by}"
        return sql

    def get_query(self, columns: str) -> Tuple[str, List[str]]:
        return self.build_select(columns), list(self.params)
