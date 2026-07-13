# AI Study Guide Generator

A Python project that uses several local AI agents to generate structured programming study guides.

The project uses Google ADK to define and organise agents, LiteLLM to connect the agents to a language model, and Ollama to run the model locally.

## Current status

Task 0 is complete. The initial project structure and starter files have been created.

Task 1 is complete. The Python environment, dependencies, Ollama server and local model have been configured and tested.

Task 2 is complete. The first agent, the Explainer Agent, has been created and tested with programming topics.

Task 3 is complete. A deterministic file-writing tool has been implemented, tested independently and connected to the project workflow.

Task 4 is complete. A deterministic validation tool now checks generated Markdown for eight required sections before the file-writing tool is allowed to save it. Invalid output is rejected and the missing sections are reported.

## Project structure

```text
ai-agents-intro/
├── agents/
│   ├── __init__.py
│   ├── explainer_agent.py
│   ├── practice_designer_agent.py
│   └── reviewer_agent.py
├── tools/
│   ├── __init__.py
│   ├── file_writer.py
│   └── validation.py
├── output/
│   └── study_guide.md
├── data/
│   └── topic_examples.json
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── main.py
```

## Planned project workflow

The completed application will:

1. Receive a programming topic.
2. Generate a simple explanation and key concepts.
3. Create an example and practice exercise.
4. Identify common mistakes.
5. Review the generated content.
6. Validate the required Markdown sections.
7. Save the result in `output/study_guide.md`.

At the current stage, the Explainer Agent, Markdown file-writing tool and validation tool have been implemented. The Practice Designer Agent, Reviewer Agent and complete multi-agent orchestration will be added in later tasks.

## Model configuration

The project currently uses:

* Model provider: Ollama
* Model connector: LiteLLM
* Local model: `llama3.2:3b`
* LiteLLM model name: `ollama_chat/llama3.2:3b`
* Ollama server: `http://localhost:11434`

The model runs locally and does not require an external API key.

## Python requirements

Python 3.10 or later is required.

The Python dependencies are listed in `requirements.txt`:

```text
google-adk
litellm
python-dotenv
```

## Setup

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Project-level commands should be run from the project root:

```bash
cd ~/ai-agents-intro
```

Running commands from inside directories such as `tools/` or `agents/` can cause package import errors.

## Installing Ollama

Ollama was installed inside WSL.

The installer initially failed because the `zstd` package was missing. The problem was fixed with:

```bash
sudo apt update
sudo apt install zstd -y
```

Ollama was then installed with:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Starting Ollama in WSL

The current WSL environment does not use `systemd`, so Ollama cannot be started with:

```bash
sudo systemctl start ollama
```

Instead, start the Ollama server manually in a separate WSL terminal:

```bash
ollama serve
```

That terminal must remain open while the project is running.

Open another WSL terminal for the project:

```bash
cd ~/ai-agents-intro
source .venv/bin/activate
```

## Downloading the local model

Download the selected model:

```bash
ollama pull llama3.2:3b
```

List the locally installed models:

```bash
ollama list
```

Inspect the selected model:

```bash
ollama show llama3.2:3b
```

## Environment variables

Create the local environment file from the example:

```bash
cp .env.example .env
```

Both `.env.example` and the local `.env` use:

```env
OLLAMA_API_BASE=http://localhost:11434
MODEL_NAME=ollama_chat/llama3.2:3b
```

The real `.env` file must not be committed because it may contain private configuration.

The `.env` file and the virtual environment are ignored by Git:

```bash
git check-ignore .env .venv
```

Expected output:

```text
.env
.venv
```

The `.env.example` file is not ignored and can be committed safely.

## Testing Ollama directly

Test the model directly through Ollama:

```bash
ollama run llama3.2:3b \
    "Explain a Python list in one short sentence."
```

## Testing LiteLLM with Ollama

LiteLLM was tested with the following script:

```bash
python - <<'PY'
import os

from dotenv import load_dotenv
from litellm import completion

load_dotenv(".env")

response = completion(
    model=os.environ["MODEL_NAME"],
    messages=[
        {
            "role": "user",
            "content": (
                "Explain a Python dictionary in one short sentence."
            ),
        }
    ],
)

print(response.choices[0].message.content)
PY
```

This confirmed the complete local connection:

```text
Python → LiteLLM → Ollama → llama3.2:3b
```

Using `load_dotenv(".env")` is intentional. Calling `load_dotenv()` without an explicit path inside a Python heredoc caused an `AssertionError`.

## Task 2: Explainer Agent

The Explainer Agent is defined in:

```text
agents/explainer_agent.py
```

Its role is to explain programming topics clearly for beginner students.

The agent receives one programming topic and attempts to return a complete Markdown study guide containing these exact level-two headings:

```markdown
## Topic
## Simple Explanation
## Key Concepts
## Example
## Practice Exercise
## Common Mistakes
## Review Comments
## Final Summary
```

The exact heading names matter because the Task 4 validator checks them deterministically.

The agent uses the model configured through the `MODEL_NAME` environment variable.

## Running the Explainer Agent

Make sure Ollama is already running in a separate terminal:

```bash
ollama serve
```

Then activate the project environment:

```bash
cd ~/ai-agents-intro
source .venv/bin/activate
```

Run the agent by passing a programming topic to `main.py`:

```bash
python main.py "Python list comprehensions"
```

Another example:

```bash
python main.py "HTTP status codes"
```

Topics containing spaces should be placed inside quotation marks.

The generated response is displayed in the terminal and checked by the validation tool.

If every required heading is present, the response is saved to:

```text
output/study_guide.md
```

If validation fails, the missing sections are printed and the invalid response is not saved. Each successful run replaces the previous contents of the output file.

## Topics tested

The Explainer Agent was successfully tested with:

* Python list comprehensions
* HTTP status codes

Both tests returned structured explanations from the local model.

## Example output

The following output was generated locally for the topic `Python list comprehensions`:

````markdown
### explainer_agent

### Explanation
List comprehensions in Python are a concise way to create new lists by performing operations on existing lists or other iterables. They provide a more readable and efficient alternative to traditional for loops. By using list comprehensions, you can write cleaner code that's easier to understand and maintain.

### Key concepts
* **Syntax**: List comprehensions consist of brackets containing the expression or expressions and an optional `for` or `if` clause.
* **Iteration**: Loops, conditions and functions can be used inside list comprehensions.
* **Filtering**: An `if` clause can filter elements before they are included in the new list.

### Example

```python
# Create a new list containing square numbers
numbers = [1, 2, 3, 4, 5]
squares = [n ** 2 for n in numbers]

print(squares)
# Output: [1, 4, 9, 16, 25]
```

This example uses a list comprehension to create a new list called `squares` containing the square of each number in `numbers`.
````

## Task 2 validation

The following requirements have been completed:

* [x] Created `agents/explainer_agent.py`
* [x] Gave the agent a clear role
* [x] Gave the agent specific instructions
* [x] Allowed the agent to receive a topic through `main.py`
* [x] Returned a structured explanation
* [x] Tested the agent with at least two topics
* [x] Saved one example output in `README.md`

## Task 3: Markdown file-writing tool

Task 3 adds a deterministic tool that saves generated Markdown content to disk.

The tool is defined in:

```text
tools/file_writer.py
```

It contains the following function:

```python
"""Utilities for saving generated Markdown content."""

from pathlib import Path


def save_markdown_file(file_path: str, content: str) -> str:
    """Save Markdown content to a file and return a useful result."""
    path = Path(file_path)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        return f"Could not save Markdown file: {error}"

    return f"Markdown file saved successfully: {path.resolve()}"
```

### How the tool works

`Path(file_path)` converts the supplied string into a `Path` object.

```python
path.parent.mkdir(parents=True, exist_ok=True)
```

This creates the parent directory when it does not already exist. The `parents=True` argument also creates missing intermediate directories, while `exist_ok=True` prevents an error when the directory already exists.

```python
path.write_text(content, encoding="utf-8")
```

This writes the Markdown content to the requested file. If the file already exists, its previous contents are replaced.

The `try` and `except` block handles ordinary file-system errors gracefully and returns a clear message instead of allowing an unhandled error to terminate the program.

The tool is independent from Google ADK, LiteLLM and Ollama. It can therefore be tested and reused without running an agent or language model.

## Testing the file-writing tool directly

The tool was tested independently before being connected to the agent workflow.

Run this command from the project root:

```bash
cd ~/ai-agents-intro
source .venv/bin/activate
```

Then run:

```bash
python - <<'PY'
from tools.file_writer import save_markdown_file

result = save_markdown_file(
    "output/direct_test/test.md",
    "# Direct tool test\n\nThe file-writing tool works.\n",
)

print(result)
PY
```

Expected result:

```text
Markdown file saved successfully: /home/aleksandre/ai-agents-intro/output/direct_test/test.md
```

The exact absolute path may differ between systems.

Check the generated file:

```bash
cat output/direct_test/test.md
```

Expected content:

```markdown
# Direct tool test

The file-writing tool works.
```

The nested `output/direct_test/` directory is created automatically by the function.

The temporary test directory can then be removed:

```bash
rm -r output/direct_test
```

## Import error encountered during direct testing

The direct test initially failed with:

```text
ModuleNotFoundError: No module named 'tools'
```

The command had been run from:

```text
~/ai-agents-intro/tools
```

From inside that directory, Python could not locate `tools` as a top-level package because the project root was not on the import path.

The problem was fixed by returning to the project root:

```bash
cd ~/ai-agents-intro
```

The direct test then worked correctly.

Project-level commands that import packages such as:

```python
from tools.file_writer import save_markdown_file
```

should therefore be run from:

```text
~/ai-agents-intro
```

## Connecting the tool to the agent workflow

`main.py` imports the tool:

```python
from tools.file_writer import save_markdown_file
```

After the Explainer Agent returns its response, `main.py` passes the response to `save_markdown_file()` and saves it in:

```text
output/study_guide.md
```

Task 3 originally connected the generated response directly to the file-writing tool. Task 4 has now inserted validation before saving:

```text
Programming topic
        ↓
main.py
        ↓
Explainer Agent
        ↓
Generated Markdown response
        ↓
validate_required_sections()
        ↓
Valid? ── no ──→ report missing sections and stop
  │
 yes
  ↓
save_markdown_file()
        ↓
output/study_guide.md
```

## Testing the complete workflow

Start Ollama in one WSL terminal:

```bash
ollama serve
```

In a second WSL terminal:

```bash
cd ~/ai-agents-intro
source .venv/bin/activate
python main.py "Python list comprehensions"
```

The generated explanation is printed in the terminal and then validated.

A successful run ends with messages similar to:

```text
Validation passed: all required sections are present.
Markdown file saved successfully: /home/aleksandre/ai-agents-intro/output/study_guide.md
```

Verify the file:

```bash
ls -l output/study_guide.md
cat output/study_guide.md
grep '^## ' output/study_guide.md
```

An invalid model response is not saved. Instead, the program reports the missing headings and exits.

## Task 3 validation

The following requirements have been completed:

* [x] Created `tools/file_writer.py`
* [x] Implemented `save_markdown_file()`
* [x] Made the function receive a path and Markdown content
* [x] Made the function create missing parent directories
* [x] Made the function write Markdown content to disk
* [x] Added basic file-writing error handling
* [x] Kept the tool independent from the agent framework
* [x] Tested the function without using the agent
* [x] Connected the function to the Explainer Agent workflow
* [x] Saved generated agent output
* [x] Confirmed that the generated file appears in `output/`

## Task 4: Validation tool

Generated model output can be incomplete or poorly structured. A language model is useful for flexible generation, but ordinary Python code is more reliable for checking fixed structural rules.

The validation tool does not decide whether an explanation is perfect. It checks only whether all required Markdown headings exist exactly as expected.

The tool is defined in:

```text
tools/validation.py
```

### Required sections

```python
REQUIRED_SECTIONS = [
    "Topic",
    "Simple Explanation",
    "Key Concepts",
    "Example",
    "Practice Exercise",
    "Common Mistakes",
    "Review Comments",
    "Final Summary",
]
```

Capitalisation and heading level matter. For example:

```markdown
## Simple Explanation
```

is accepted, while these are rejected by the strict validator:

```markdown
### Simple Explanation
## simple explanation
## Explanation
```

### Validation implementation

```python
"""Utilities for validating generated Markdown study guides."""


REQUIRED_SECTIONS = [
    "Topic",
    "Simple Explanation",
    "Key Concepts",
    "Example",
    "Practice Exercise",
    "Common Mistakes",
    "Review Comments",
    "Final Summary",
]


def validate_required_sections(markdown: str) -> dict:
    """Check whether Markdown contains all required level-two headings."""
    headings = {
        line.strip()
        for line in markdown.splitlines()
        if line.strip().startswith("## ")
    }

    missing_sections = [
        section
        for section in REQUIRED_SECTIONS
        if f"## {section}" not in headings
    ]

    return {
        "valid": not missing_sections,
        "missing_sections": missing_sections,
    }
```

### How the validator works

`markdown.splitlines()` separates the Markdown into individual lines.

```python
if line.strip().startswith("## ")
```

This keeps headings that begin with two hash characters followed by a space.

The validator then checks every name in `REQUIRED_SECTIONS`. Any exact heading that was not found is added to `missing_sections`.

A valid result looks like:

```python
{
    "valid": True,
    "missing_sections": [],
}
```

An invalid result looks like:

```python
{
    "valid": False,
    "missing_sections": ["Example", "Final Summary"],
}
```

`not missing_sections` is `True` when the list is empty and `False` when the list contains one or more missing sections.

### Testing valid Markdown

A single-line command avoids unfinished heredocs, triple-quoted strings and embedded Markdown code fences:

```bash
python -c 'from tools.validation import validate_required_sections; markdown="## Topic\n\nPython dictionaries\n\n## Simple Explanation\n\nA dictionary stores key-value pairs.\n\n## Key Concepts\n\nKeys and values.\n\n## Example\n\nA simple dictionary example.\n\n## Practice Exercise\n\nCreate a dictionary describing a book.\n\n## Common Mistakes\n\nUsing a key that does not exist.\n\n## Review Comments\n\nThe guide is clear.\n\n## Final Summary\n\nDictionaries connect keys with values."; print(validate_required_sections(markdown))'
```

Expected result:

```text
{'valid': True, 'missing_sections': []}
```

### Testing incomplete Markdown

```bash
python -c 'from tools.validation import validate_required_sections; print(validate_required_sections("## Topic\n\nPython dictionaries\n\n## Example\n\nA simple example."))'
```

Expected result:

```text
{'valid': False, 'missing_sections': ['Simple Explanation', 'Key Concepts', 'Practice Exercise', 'Common Mistakes', 'Review Comments', 'Final Summary']}
```

The missing names are returned in the same order as `REQUIRED_SECTIONS`.

### Heredoc issue encountered during testing

The first tests began with:

```bash
python - <<'PY'
```

The terminal displayed a `>` prompt and appeared to be frozen. It was actually waiting for the unfinished command because the triple-quoted Python string, embedded Markdown code block or final `PY` marker had not been closed.

Press `Ctrl+C` to cancel an unfinished command. The final `PY` marker must be alone on its line with no indentation. The tests were changed to `python -c` commands to avoid this problem.

### Connecting validation to `main.py`

`main.py` imports both deterministic tools:

```python
from tools.file_writer import save_markdown_file
from tools.validation import validate_required_sections
```

After receiving the agent response, it validates it:

```python
validation_result = validate_required_sections(response)
```

Invalid output is reported and not saved:

```python
if not validation_result["valid"]:
    missing_sections = ", ".join(
        validation_result["missing_sections"]
    )

    print("\nValidation failed.")
    print(f"Missing sections: {missing_sections}")
    print("The study guide was not saved.")
    raise SystemExit(1)
```

Valid output is passed to the file-writing tool:

```python
print("\nValidation passed: all required sections are present.")

save_result = save_markdown_file(
    str(OUTPUT_FILE),
    response,
)

print(save_result)
```

### Stricter agent prompt

The Explainer Agent was updated to copy an exact eight-heading template. The same heading list is also included in the immediate prompt created by `main.py`:

```text
## Topic
## Simple Explanation
## Key Concepts
## Example
## Practice Exercise
## Common Mistakes
## Review Comments
## Final Summary
```

This duplication is intentional. The local `llama3.2:3b` model sometimes follows the immediate user message more reliably than a longer general agent instruction.

### Invalid model output encountered

During testing, the model produced output such as:

```markdown
## Python List Comprehensions
### Simple Explanation
### Key Concepts
### Example
```

It also omitted `Final Summary` in some responses.

The validator correctly rejected this output because `## Python List Comprehensions` is not `## Topic`, the other headings used `###` instead of `##`, and the final required heading was absent.

The terminal reported:

```text
Validation failed.
Missing sections: Topic, Simple Explanation, Key Concepts, Example, Practice Exercise, Common Mistakes, Review Comments, Final Summary
The study guide was not saved.
```

This is correct behaviour. Task 4 is meant to detect malformed output rather than silently save it.

### Checking the complete workflow

Check the Python files for syntax errors:

```bash
python -m py_compile \
    tools/validation.py \
    agents/explainer_agent.py \
    main.py
```

No output means Python found no syntax errors.

Run the project:

```bash
python main.py "Python list comprehensions"
```

A successful run must finish with:

```text
Validation passed: all required sections are present.
Markdown file saved successfully: ...
```

Check the saved headings:

```bash
grep '^## ' output/study_guide.md
```

Expected:

```text
## Topic
## Simple Explanation
## Key Concepts
## Example
## Practice Exercise
## Common Mistakes
## Review Comments
## Final Summary
```

### Task 4 validation

The following requirements have been completed:

* [x] Created `tools/validation.py`
* [x] Implemented `validate_required_sections()`
* [x] Made the function receive Markdown content
* [x] Checked all required sections
* [x] Returned whether the content is valid
* [x] Returned the missing section names
* [x] Tested complete Markdown
* [x] Tested incomplete Markdown
* [x] Connected the validator to the project workflow
* [x] Ran validation after generation
* [x] Prevented invalid Markdown from being saved
* [x] Updated the agent prompts to match the validator
* [x] Confirmed that malformed model output is detected and reported

## Current limitations

The Explainer Agent, Markdown file-writing tool and validation tool have been implemented.

The Practice Designer Agent, Reviewer Agent and complete multi-agent orchestration will be implemented in later tasks.

The validator checks structure only. It does not decide whether the explanation is factually correct, whether the example is useful, or whether the exercise has the right difficulty.

Because `llama3.2:3b` is a small local model, its formatting may still vary between runs. It may rename headings, use `###` instead of `##`, or omit a section. The validator now catches these problems and prevents invalid output from replacing `output/study_guide.md`.

The current design separates responsibilities:

```text
AI model          → flexible content generation
Python validator  → predictable structural checking
File-writing tool → predictable file-system operation
```

This is the main lesson from Task 4: use the model for flexible language generation and deterministic Python code for rules that must be checked consistently.
