# querymd

#### Example usage
```
# Initialize the QueryBuilder with a table name
query_builder = QueryBuilder("sales_data")

# Set the time grain for the query
query_builder.set_time_grain(TimeGrain("sale_date", "month", "Sale Month"))

# Add slice columns
query_builder.add_slice(Slice("region", "Sales Region"))
query_builder.add_slice(Slice("product_category", "Product Category"))

# Add measure columns
query_builder.add_measure(Measure("SUM(revenue)", "Total Revenue"))
query_builder.add_measure(Measure("COUNT(distinct customer_id)", "Unique Customers"))

# Add ratio metrics
query_builder.add_ratio(Ratio("SUM(revenue)", "COUNT(distinct customer_id)", "Revenue per Customer"))

# Add list filter
query_builder.add_filter(Filter("region", ["East", "West"], "list"))

# Add custom filter
query_builder.add_filter(Filter("sale_date", custom_expression="sale_date >= '2023-01-01' AND sale_date < '2023-04-01'", filter_type="custom"))

# Remove a slice component by its nice name (for demonstration)
query_builder.remove_component("Product Category")

# Change the table name (for demonstration)
query_builder.set_table_name("updated_sales_data")

# Compile the query
compiled_query = query_builder.compile()

# Print the compiled query
print(compiled_query)
```

#### Example output
```
SELECT
  date_trunc('month', sale_date) AS "Sale Month",
  region AS "Sales Region",
  SUM(revenue) AS "Total Revenue",
  COUNT(distinct customer_id) AS "Unique Customers",
  (SUM(revenue)) / NULLIF(COUNT(distinct customer_id), 0) AS "Revenue per Customer"
FROM updated_sales_data
WHERE TRUE AND
  region IN ('East', 'West')
 AND
  sale_date >= '2023-01-01' AND sale_date < '2023-04-01'
GROUP BY 1, 2
ORDER BY 1 DESC, 2
```
