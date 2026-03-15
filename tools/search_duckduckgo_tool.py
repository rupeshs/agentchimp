from ddgs import DDGS
from tools.abstract_tool import AbstractTool


class DuckDuckGoSearchTool(AbstractTool):
    """Web search tool using DuckDuckGo — no API key required."""

    def __init__(self, max_results: int = 5):
        self.max_results = max_results

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web using DuckDuckGo. Returns titles, URLs, and snippets "
            "for the most relevant results. No API key required."
        )

    def get_parameters_schema(self) -> dict:
        return {
            "query": {
                "type": "string",
                "description": "Search the web for current, real-time information. Always use this for any question about current events, people, prices, or anything that may have changed recently.",
            },
            "region": {
                "type": "string",
                "description": (
                    "Region code for localized results "
                    "(e.g. 'us-en', 'in-en', 'uk-en', 'wt-wt' for no region). "
                    "Defaults to 'wt-wt'."
                ),
            },
        }

    # def to_schema(self) -> dict:
    #     """Override to mark only 'query' as required."""
    #     return {
    #         "type": "function",
    #         "function": {
    #             "name": self.name,
    #             "description": self.description,
    #             "parameters": {
    #                 "type": "object",
    #                 "properties": self.get_parameters_schema(),
    #                 "required": ["query"],
    #             },
    #         },
    #     }

    def execute(self, **kwargs) -> str:
        query: str = kwargs.get("query")
        region: str = kwargs.get("region", "wt-wt")

        if not query:
            return "Error: 'query' parameter is required."

        try:
            with DDGS() as ddgs:
                raw_results = list(
                    ddgs.text(
                        query,
                        region=region,
                        safesearch="off",
                        max_results=self.max_results,
                    )
                )
        except Exception as e:
            return f"Search failed: {str(e)}"

        return self._format_results(query, raw_results)

    def _format_results(self, query: str, results: list) -> str:
        if not results:
            return f"No results found for query: '{query}'"

        parts = [f"Search results for: '{query}'\n"]
        for i, result in enumerate(results, start=1):
            title = result.get("title", "No title")
            url = result.get("href", "No URL")
            snippet = result.get("body", "No description available.")
            parts.append(f"{i}. {title}\n   URL: {url}\n   {snippet}\n")

        return "\n".join(parts)
