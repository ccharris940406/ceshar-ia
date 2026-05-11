from dotenv import load_dotenv

load_dotenv(override=True)

from mcp.server.fastmcp import FastMCP

from mcp_server.tools.github import register_github_tool

mcp = FastMCP("github-tools", "0.1.0")
register_github_tool(mcp)


@mcp.tool()
def hello() -> str:
    """Returns a greeting message."""
    return "Hello, world!"


if __name__ == "__main__":
    print("Running MCP server...")
    mcp.run()
