import urllib.request
from tools.abstract_tool import AbstractTool


class WebFetchTool(AbstractTool):
    JINA_PREFIX = "https://r.jina.ai/"
    MAX_RESULT_CHARS = 6000

    @property
    def name(self) -> str:
        return "web_fetch"

    @property
    def description(self) -> str:
        return (
            "Fetch the content of a web page. "
            "Uses Jina Reader to extract content from any URL. "
            "Use format='html' for raw HTML or format='markdown' for clean readable text (default)."
        )

    def get_parameters_schema(self) -> dict:
        return {
            "url": {
                "type": "string",
                "description": "The URL of the web page to fetch",
            },
            "format": {
                "type": "string",
                "description": "Response format: 'markdown' (default) or 'html'",
                "enum": ["markdown", "html"],
            },
        }

    def get_required_parameters(self) -> list[str]:
        return ["url"]

    def execute(self, **kwargs) -> str:
        url = kwargs.get("url")
        if not url:
            return "Error: 'url' parameter is required."

        fmt = kwargs.get("format", "markdown")
        jina_url = self.JINA_PREFIX + url

        headers = {"User-Agent": "AgentChimp/1.0"}
        if fmt == "html":
            headers["x-respond-with"] = "html"

        try:
            req = urllib.request.Request(jina_url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode("utf-8")
            if len(content) > self.MAX_RESULT_CHARS:
                content = content[: self.MAX_RESULT_CHARS] + "\n\n[Content truncated]"
            return content
        except urllib.error.HTTPError as e:
            return f"HTTP error {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return f"URL error: {e.reason}"
        except Exception as e:
            return f"Exception: {str(e)}"
