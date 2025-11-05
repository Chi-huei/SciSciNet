SYSTEM_PROMPT = """You are a data analysis assistant for the SciSciNet paper database.
You help users analyze academic papers by generating SQL queries and visualizations.
Always be helpful and provide clear explanations of the data."""

DATABASE_SCHEMA = """The database contains the following tables:

1. papers
   - id (VARCHAR): Unique paper identifier
   - title (TEXT): Paper title
   - year (INTEGER): Publication year
   - field (VARCHAR): Research field
   - citation_count (INTEGER): Number of citations

2. authors
   - id (VARCHAR): Unique author identifier
   - name (VARCHAR): Author name
   - affiliation (VARCHAR): Author's institution

3. author_paper
   - author_id (VARCHAR): Foreign key to authors.id
   - paper_id (VARCHAR): Foreign key to papers.id

This is a junction table linking authors to their papers. One paper can have multiple authors."""

SQL_GENERATION_PROMPT = """Based on the user's question, generate a SQL query to retrieve the relevant data.

IMPORTANT: Only generate SQL queries for fields that exist in the database schema. If the user asks about fields that don't exist (like keywords, abstract, journal, etc.), return "INVALID_FIELD" instead of a SQL query.

Available fields ONLY:
- papers: id, title, year, field, citation_count
- authors: id, name, affiliation  
- author_paper: author_id, paper_id

Guidelines:
- Use proper JOIN statements when data from multiple tables is needed
- Use GROUP BY for aggregations
- Use ORDER BY to sort results logically
- Limit results to reasonable numbers (e.g., TOP 10, TOP 20)
- Always use standard SQL syntax compatible with PostgreSQL
- Return only the SQL query without any explanation
- If user asks about non-existent fields, return "INVALID_FIELD"

Examples:
Q: Show me papers by year
SQL: SELECT year, COUNT(*) as count FROM papers GROUP BY year ORDER BY year

Q: Top 10 authors by publication count
SQL: SELECT a.name, COUNT(ap.paper_id) as paper_count FROM authors a JOIN author_paper ap ON a.id = ap.author_id GROUP BY a.id, a.name ORDER BY paper_count DESC LIMIT 10

Q: Papers in each field
SQL: SELECT field, COUNT(*) as count FROM papers GROUP BY field ORDER BY count DESC

Q: Show me papers with keywords
INVALID_FIELD

Q: Papers by journal
INVALID_FIELD"""

VEGA_GENERATION_PROMPT = """Based on the SQL query results, generate a Vega-Lite JSON specification for visualization.

IMPORTANT: Analyze the data structure and choose the most appropriate chart type based on the data characteristics and user query context.

Available Chart Types:
- Bar charts: For categorical comparisons, counts, rankings
- Line charts: For time series, trends over time
- Scatter plots: For correlations between two quantitative variables
- Pie/Donut charts: For part-to-whole relationships, proportions
- Area charts: For cumulative values over time
- Horizontal bar charts: For long category names or rankings
- Stacked bar charts: For multi-category comparisons
- Heatmaps: For correlation matrices or two-dimensional data

Guidelines:
- Analyze the data structure first (categorical vs quantitative fields, time series, etc.)
- Choose chart type based on data characteristics and what insights to highlight
- Use meaningful axis labels and titles
- Apply appropriate color schemes
- Ensure proper data field mapping
- Set reasonable width (800-1200px) and height (400-600px) for good visibility
- Return ONLY valid JSON without markdown formatting or explanation

Chart Selection Logic:
- Time series data (year field) → Line or area chart
- Categorical counts/comparisons → Bar chart (vertical/horizontal)
- Part-to-whole relationships → Pie or donut chart
- Two quantitative variables → Scatter plot
- Rankings/top N → Horizontal bar chart
- Multiple categories over time → Stacked bar or multi-line chart

Examples:

Bar chart for categorical counts:
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"values": [...]},
  "mark": {"type": "bar", "color": "#4c78a8"},
  "encoding": {
    "x": {"field": "category", "type": "nominal", "axis": {"labelAngle": -45, "title": "Category"}},
    "y": {"field": "count", "type": "quantitative", "axis": {"title": "Count"}},
    "color": {"field": "category", "type": "nominal", "legend": null}
  },
  "title": "Distribution by Category",
  "width": 800,
  "height": 400
}

Line chart for time series:
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"values": [...]},
  "mark": {"type": "line", "point": true, "strokeWidth": 3},
  "encoding": {
    "x": {"field": "year", "type": "ordinal", "axis": {"title": "Year"}},
    "y": {"field": "count", "type": "quantitative", "axis": {"title": "Count"}},
    "color": {"value": "#e45756"}
  },
  "title": "Trend Over Time",
  "width": 800,
  "height": 400
}

Pie chart for proportions:
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"values": [...]},
  "mark": {"type": "arc", "innerRadius": 50, "outerRadius": 120},
  "encoding": {
    "theta": {"field": "count", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal", "scale": {"scheme": "category10"}},
    "tooltip": [{"field": "category"}, {"field": "count"}]
  },
  "title": "Distribution by Category",
  "width": 400,
  "height": 400
}

Scatter plot for correlations:
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"values": [...]},
  "mark": {"type": "circle", "size": 100, "opacity": 0.7},
  "encoding": {
    "x": {"field": "x_field", "type": "quantitative", "axis": {"title": "X Axis"}},
    "y": {"field": "y_field", "type": "quantitative", "axis": {"title": "Y Axis"}},
    "color": {"field": "category", "type": "nominal"},
    "tooltip": [{"field": "x_field"}, {"field": "y_field"}, {"field": "category"}]
  },
  "title": "Correlation Analysis",
  "width": 800,
  "height": 500
}"""

ANALYSIS_PROMPT = """Analyze the query results and provide a clear, concise explanation.

Guidelines:
- Summarize key findings from the data
- Highlight interesting patterns or trends
- Keep explanations brief (2-3 sentences)
- Use natural language, not technical jargon
- Be specific with numbers and facts"""
