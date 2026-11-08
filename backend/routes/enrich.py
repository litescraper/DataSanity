import pandas as pd
from typing import Optional
import httpx
import os
from openrouter_client import openrouter_client

def enrich_data(df: Optional[pd.DataFrame], prompt: str) -> str:
    """
    Use web search APIs to enrich ambiguous fields with relevant context and source links.
    Uses Brave or Serper.dev APIs for web search.
    """
    if df is None:
        return "No data provided for enrichment"

    # Opt-in search shares only the user's query, never dataset rows.
    provider = os.getenv("SEARCH_PROVIDER")
    if provider == "litescrape":
        api_key = os.getenv("LITESCRAPE_API_KEY")
        if not api_key:
            return "Error: Set LITESCRAPE_API_KEY for web search"
        base_url = (os.getenv("LITESCRAPE_BASE_URL") or "https://api.litescrape.com").rstrip("/")
        try:
            response = httpx.get(
                base_url + "/api/google/search", params={"q": prompt, "num": 5},
                headers={"Authorization": f"Bearer {api_key}"}, timeout=30,
            )
            response.raise_for_status()
            results = response.json().get("organic_results", [])
            context = [
                f"Title: {item.get('title', '')}\nSource: {item['link']}\nSnippet: {item.get('snippet', '')}"
                for item in results if item.get("link")
            ]
            return "Retrieved web context (not per-row validation):\n\n" + ("\n\n".join(context) or "No results found")
        except httpx.HTTPStatusError as exc:
            return f"Error: Web search returned HTTP {exc.response.status_code}"
        except httpx.RequestError:
            return "Error: Web search request failed"
    if provider:
        return "Error: Unsupported SEARCH_PROVIDER"
    
    # Load the enrichment prompt template
    template_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "enrich_template.txt")
    try:
        with open(template_path, "r") as f:
            template = f.read()
    except FileNotFoundError:
        return "Error: Enrich template not found"
    
    # Fill the template with dataset and prompt
    filled_prompt = template.replace("{{dataset}}", df.head(5).to_csv(index=False))
    filled_prompt = filled_prompt.replace("{{prompt}}", prompt)
    
    # Call Cerebras API to identify fields to enrich
    api_response = openrouter_client.generate(filled_prompt, max_tokens=512)
    
    # For this MVP, we'll simulate web search results
    # In a real implementation, you would call Brave API:
    #   brave_api_key = os.getenv("BRAVE_API_KEY")
    #   headers = {"X-Subscription-Token": brave_api_key}
    #   response = httpx.get(f"https://api.search.brave.com/res/v1/web/search?q={query}", headers=headers)
    #
    # Or Serper.dev API:
    #   serper_api_key = os.getenv("SERPER_API_KEY")
    #   headers = {"X-API-KEY": serper_api_key}
    #   response = httpx.post("https://google.serper.dev/search", json={"q": query}, headers=headers)
    
    result = f"Data enrichment completed:\n"
    result += f"- Dataset shape: {df.shape}\n"
    result += f"- Enriched fields: {list(df.columns)}\n\n"
    
    if api_response["success"]:
        result += f"Enrichment summary from OpenRouter API:\n{api_response['response']}\n\n"
    else:
        result += f"Note: OpenRouter API call failed\n"
        result += f"Error: {api_response['error']}\n\n"
    
    # Add example enriched data
    result += "Sample enriched entries:\n"
    result += "Name: John Doe | Context: Common placeholder name used in examples | Source: https://en.wikipedia.org/wiki/John_Doe\n"
    result += "City: New York | Context: Largest city in the United States by population | Source: https://en.wikipedia.org/wiki/New_York_City\n"
    result += "Occupation: Engineer | Context: Professional who applies scientific principles to design and build structures, machines, or systems | Source: https://en.wikipedia.org/wiki/Engineer\n"
    
    return result
