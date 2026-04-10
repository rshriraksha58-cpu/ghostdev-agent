import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def generate_completion(context: dict, target_file: str, file_content: str) -> str:
    """Send context + file to Claude and get completed code back."""

    prompt = f"""You are GhostDev, a silent AI developer working autonomously on a codebase.

PROJECT CONTEXT:
- Goals: {context.get('goals', 'Not specified')}
- README: {context.get('readme', 'Not found')}
- Recent commits: {context.get('commits', 'No history')}
- TODOs found across repo: {context.get('todos', 'None')}

CURRENT FILE: {target_file}
{file_content}

YOUR TASKS:
1. Complete every stub function (functions with only `pass` or empty body)
2. Implement every TODO / FIXME comment in the code
3. Fix any obvious bugs you can identify
4. Add missing imports if needed
5. Match the existing code style exactly

RULES:
- Return ONLY the completed Python file content
- Do NOT include any explanation, markdown, or code fences
- Do NOT remove existing code — only add or fix
- Keep all existing comments
- If a function is already complete, leave it exactly as is
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def generate_bug_fix(context: dict, target_file: str, file_content: str, error: str) -> str:
    """Ask Claude to fix a specific error in a file."""

    prompt = f"""You are GhostDev, a silent AI developer.

A file has a bug that is preventing it from running. Fix it.

FILE: {target_file}
{file_content}

ERROR:
{error}

PROJECT GOALS: {context.get('goals', 'Not specified')}

RULES:
- Return ONLY the fixed Python file content
- Do NOT include any explanation, markdown, or code fences
- Fix the error and any related issues you spot
- Do not change logic that is unrelated to the bug
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
