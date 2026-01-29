QUERY_EXPANDER_PROMPT = """
You are a query expansion utility.
Your task is to expand the given research query into a richer,
search-oriented query with additional context.
Query:
{query}

Additional context / constraints (if any):
{extra}

Generate a concise hypothetical answer.
"""