import base64
import os

import httpx
from langchain_core.tools import StructuredTool
from mcp.server.fastmcp import FastMCP


def _get_headers() -> dict:
    return {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json",
    }


def _get_user() -> str:
    return os.getenv("GITHUB_USER", "")


def list_repos() -> str:
    """Lista los repositorios públicos de Carlos en GitHub"""
    response = httpx.get(
        f"https://api.github.com/users/{_get_user()}/repos",
        headers=_get_headers(),
    )
    repos = response.json()
    return "\n".join(
        f"- {r['name']}: {r['description'] or 'No description'}" for r in repos
    )


def get_repo(repo: str) -> str:
    """Obtiene los detalles de un repositorio específico"""
    response = httpx.get(
        f"https://api.github.com/repos/{_get_user()}/{repo}",
        headers=_get_headers(),
    )
    r = response.json()
    return (
        f"Nombre: {r['name']}\n"
        f"Descripción: {r.get('description', 'N/A')}\n"
        f"Lenguaje: {r.get('language', 'N/A')}\n"
        f"Stars: {r.get('stargazers_count', 0)}\n"
        f"URL: {r.get('html_url', 'N/A')}"
    )


def get_languages(repo: str) -> str:
    """Obtiene los lenguajes de programación usados en un repositorio"""
    response = httpx.get(
        f"https://api.github.com/repos/{_get_user()}/{repo}/languages",
        headers=_get_headers(),
    )
    languages = response.json()
    return "\n".join(f"- {lang}: {bytes_} bytes" for lang, bytes_ in languages.items())


def get_readme(repo: str) -> str:
    """Obtiene el contenido del README de un repositorio"""
    response = httpx.get(
        f"https://api.github.com/repos/{_get_user()}/{repo}/readme",
        headers=_get_headers(),
    )
    if response.status_code != 200:
        return "README no encontrado"
    content = response.json().get("content", "")
    return base64.b64decode(content).decode("utf-8")


def get_github_tools() -> list[StructuredTool]:
    return [
        StructuredTool.from_function(list_repos),
        StructuredTool.from_function(get_repo),
        StructuredTool.from_function(get_languages),
        StructuredTool.from_function(get_readme),
    ]


def register_github_tool(mcp: FastMCP) -> None:
    mcp.tool()(list_repos)
    mcp.tool()(get_repo)
    mcp.tool()(get_languages)
    mcp.tool()(get_readme)
