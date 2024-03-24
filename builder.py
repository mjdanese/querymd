class QueryComponent:
    def to_sql(self):
        raise NotImplementedError

class TimeGrain(QueryComponent):
    def __init__(self, column, grain, nice_name):
        self.column = column
        self.grain = grain
        self.nice_name = nice_name

    def to_sql(self):
        return f"date_trunc('{self.grain}', {self.column}) AS \"{self.nice_name}\""

class Slice(QueryComponent):
    def __init__(self, column, nice_name=None):
        self.column = column
        self.nice_name = nice_name or column

    def to_sql(self):
        return f"{self.column} AS \"{self.nice_name}\""

class Measure(QueryComponent):
    def __init__(self, expression, nice_name):
        self.expression = expression
        self.nice_name = nice_name

    def to_sql(self):
        return f"{self.expression} AS \"{self.nice_name}\""

class Ratio(QueryComponent):
    def __init__(self, numerator, denominator, nice_name):
        self.numerator = numerator
        self.denominator = denominator
        self.nice_name = nice_name

    def to_sql(self):
        return f"({self.numerator}) / NULLIF({self.denominator}, 0) AS \"{self.nice_name}\""

class Filter(QueryComponent):
    def __init__(self, column, value=None, filter_type="list", custom_expression=None):
        """
        Initializes a new filter component.
        
        :param column: The column name to apply the filter on.
        :param value: The list of values for the 'list' filter type.
        :param filter_type: The type of filter ('list' or 'custom').
        :param custom_expression: A custom filter expression. Required if filter_type is 'custom'.
        """
        self.column = column
        self.value = value
        self.filter_type = filter_type
        self.custom_expression = custom_expression

    def to_sql(self):
        if self.filter_type == "list":
            if not isinstance(self.value, list):
                raise ValueError("Value must be a list for 'list' filter type.")
            formatted_values = ", ".join([f"'{v}'" for v in self.value])
            return f"{self.column} IN ({formatted_values})\n"
        elif self.filter_type == "custom":
            if not self.custom_expression:
                raise ValueError("Custom expression must be provided for 'custom' filter type.")
            return self.custom_expression
        else:
            raise ValueError("Unsupported filter type.")

class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self.components = {"time_grain": None, "slices": [], "measures": [], "ratios": [], "filters": []}

    def remove_component(self, nice_name):
        """
        Removes a component by its nice_name.
        """
        # TimeGrain is a singular component, compare directly if it's not None
        if self.components["time_grain"] and self.components["time_grain"].nice_name == nice_name:
            self.components["time_grain"] = None
            return self
        
        # For other components, iterate through each list to remove the component with the matching nice_name
        for component_type in ["slices", "measures", "ratios"]:
            self.components[component_type] = [component for component in self.components[component_type] if component.nice_name != nice_name]

        return self

    def set_table_name(self, new_table_name):
        """
        Sets a new table name for the query.
        
        :param new_table_name: The new table name to use in the query.
        """
        self.table = new_table_name
        return self

    def set_time_grain(self, time_grain):
        self.components["time_grain"] = time_grain
        return self

    def add_slice(self, slice):
        self.components["slices"].append(slice)
        return self

    def add_measure(self, measure):
        if not self.components["measures"]:
            self.components["measures"].append(measure)
        else:
            self.components["measures"].append(measure)
        return self

    def add_ratio(self, ratio):
        self.components["ratios"].append(ratio)
        return self

    def add_filter(self, filter):
        self.components["filters"].append(filter)
        return self

    def compile(self):
        select_parts = [self.components["time_grain"].to_sql()] + \
                       [component.to_sql() for component in self.components["slices"]] + \
                       [component.to_sql() for component in self.components["measures"]] + \
                       [component.to_sql() for component in self.components["ratios"]]

        where_parts = ["TRUE"] + \
                      [component.to_sql() for component in self.components["filters"]]

        group_by_parts = ["1"] + [str(i + 2) for i in range(len(self.components["slices"]))]

        order_by_parts = ["1 DESC"] + [str(i + 2) for i in range(len(self.components["slices"]))]

        select_clause = "SELECT\n  " + ",\n  ".join(select_parts)
        from_clause = f"FROM {self.table}"
        where_clause = "WHERE " + " AND\n  ".join(where_parts)
        group_by_clause = "GROUP BY " + ", ".join(group_by_parts)
        order_by_clause = "ORDER BY " + ", ".join(order_by_parts)

        # Assembling the final query
        query = "\n".join([select_clause, from_clause, where_clause, group_by_clause, order_by_clause])
        return query
