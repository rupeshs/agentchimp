import os
import requests
from tools.abstract_tool import AbstractTool


class SearchTavilyTool(AbstractTool):
    @property
    def name(self) -> str:
        return "search_tavily"

    @property
    def description(self) -> str:
        return "Search the internet using Tavily and return relevant results."

    def get_parameters_schema(self) -> dict:
        return {
            "query": {
                "type": "string",
                "description": "Search query to look up on the internet",
            }
        }

    def execute(self, **kwargs) -> str:
        query = kwargs.get("query")

        if not query:
            return "Query is required."

        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            return "Tavily API key not configured."

        url = "https://api.tavily.com/search"

        payload = {"api_key": api_key, "query": query, "max_results": 5}

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                return "No results found."

            output = []
            for r in results:
                title = r.get("title", "")
                content = r.get("content", "")
                url = r.get("url", "")

                output.append(f"{title}\n{content}\n{url}")

            return "\n\n".join(output)

        except Exception as e:
            return f"Search failed: {str(e)}"
