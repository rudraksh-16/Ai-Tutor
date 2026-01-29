QUERY_EXPANDER_PROMPT = """
You are a hypothesis generator.
Generate a hypothetical document that would help answer a query.
Query:
{query}

Additional context / constraints (if any):
{extra}

Generate a concise hypothetical answer.
"""