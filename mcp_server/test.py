from dotenv import load_dotenv

from mcp_server.tools.github import get_languages, get_readme, get_repo, list_repos

load_dotenv(override=True)

print(list_repos())
print(get_repo("ceshar-ia"))
print(get_languages("ceshar-ia"))
print(get_readme("ceshar-ia"))
´
