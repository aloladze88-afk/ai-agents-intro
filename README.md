# AI Study Guide Generator

A Python project that uses several local AI agents to generate structured programming study guides.

The project uses Google ADK to define and organise agents, LiteLLM to connect the agents to a language model, and Ollama to run the model locally.

## Current status

Tasks 0 through 8 are complete.

Task 0 created the initial project structure and starter files.

Task 1 configured and tested the Python environment, dependencies, Ollama server and local model.

Task 2 created the Explainer Agent.

Task 3 added a deterministic Markdown file-writing tool.

Task 4 added deterministic validation of the required Markdown structure.

Task 5 added the Practice Designer Agent, which uses the original topic and the Explainer Agent's output.

Task 6 added the Reviewer Agent, which reviews the assembled draft instead of rewriting it.

Task 7 runs the complete sequential workflow in `main.py`. The workflow assembles the final Markdown in one place, validates it, reports missing sections clearly and saves valid output to `output/study_guide.md`.

Task 8 adds centralised configuration, empty-input checks, an Ollama preflight check, model-availability checks, explicit file-writing errors, clear validation-failure reporting and troubleshooting instructions.

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
│   ├── ollama.py
│   └── validation.py
├── output/
│   └── study_guide.md
├── data/
│   └── topic_examples.json
├── .env
├── .env.example
├── config.py
├── .gitignore
├── requirements.txt
├── README.md
└── main.py
```

## Current project workflow

The current implementation follows this explicit sequence:

```text
Topic input and empty-input check
    ↓
Configuration validation
    ↓
Ollama server and model preflight check
    ↓
Explainer Agent
    ↓
Practice Designer Agent
    ↓
Draft Study Guide
    ↓
Reviewer Agent
    ↓
Final Markdown Assembly
    ↓
Validation Tool
    ↓
Save Markdown Tool
    ↓
output/study_guide.md
```

`main.py` controls every hand-off. Each agent has a narrow responsibility:

* The Explainer Agent creates the explanatory material.
* The Practice Designer Agent receives the topic and explanation, then creates one beginner-friendly exercise.
* Ordinary Python code assembles the draft.
* The Reviewer Agent receives that assembled draft and returns review comments only.
* Ordinary Python code assembles the final Markdown in the required order.
* The validation tool checks the final headings.
* The file-writing tool saves the guide only after validation succeeds.

The final file uses this structure:

```markdown
# Topic

## Simple Explanation

## Key Concepts

## Example

## Practice Exercise

## Common Mistakes

## Review Comments

## Final Summary
```

The topic is now a level-one heading. The remaining required sections are level-two headings.

## Model configuration

The project currently uses:

* Model provider: Ollama
* Provider setting: `MODEL_PROVIDER=ollama`
* Model connector: LiteLLM
* Local model: `llama3.2:3b`
* LiteLLM model name: `ollama_chat/llama3.2:3b`
* Ollama server: `http://localhost:11434`

`config.py` loads and validates these values before any agent is created. The current project intentionally supports Ollama only. Adding another provider would require adding provider-specific validation and connection settings rather than merely changing the provider name.

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
MODEL_PROVIDER=ollama
MODEL_NAME=ollama_chat/llama3.2:3b
OLLAMA_API_BASE=http://localhost:11434
```

`MODEL_PROVIDER` selects the supported provider. `MODEL_NAME` is the LiteLLM model identifier and must keep an Ollama prefix such as `ollama_chat/`. `OLLAMA_API_BASE` is the address of the local Ollama server.

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

> **Current implementation note:** At Task 2, the Explainer Agent generated the complete guide structure. Task 7 narrows its role to the explanatory sections, while `main.py` now assembles the complete document deterministically.

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

The Explainer Agent's response is passed to the Practice Designer Agent together with the original topic. The specialised exercise then replaces the draft `Practice Exercise` section.

The combined study guide is displayed in the terminal and checked by the validation tool. If every required heading is present, it is saved to:

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

Task 3 originally connected the Explainer Agent directly to the file-writing tool. Tasks 4, 5 and 6 have expanded that workflow:

```text
Programming topic
        ↓
main.py
        ↓
Explainer Agent
        ↓
Structured draft study guide
        ↓
Practice Designer Agent
(topic + Explainer Agent output)
        ↓
Specialised practice exercise
        ↓
replace_markdown_section()
        ↓
Draft with specialised exercise
        ↓
Reviewer Agent
(topic + current draft)
        ↓
Short review comments
        ↓
replace_markdown_section()
        ↓
Completed study guide
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

> **Current implementation note:** Task 4 originally required eight level-two headings, including `## Topic`. Task 7 changes the final topic heading to `# Topic` and updates the validator accordingly. The original Task 4 code below is retained as development history.

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

After both agents have run and the exercise has been inserted, `main.py` validates the combined study guide:

```python
validation_result = validate_required_sections(study_guide)
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
    study_guide,
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
    agents/practice_designer_agent.py \
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


## Task 5: Practice Designer Agent

> **Current implementation note:** Task 5 originally inserted the exercise by replacing a placeholder section. Task 7 now extracts the specialised exercise and assembles the entire Markdown document in one place.

A multi-agent system is useful when different parts of the work have different responsibilities. The Explainer Agent focuses on explaining a topic, while the Practice Designer Agent focuses only on creating a suitable exercise.

This separation prevents the second agent from unnecessarily rewriting the explanation and makes the data flow between agents easier to understand.

The Practice Designer Agent is defined in:

```text
agents/practice_designer_agent.py
```

The filename uses underscores to match the project structure:

```text
practice_designer_agent.py
```

The self-validation wording `practicedesigneragent.py` is treated as a typo because the main task instructions explicitly require `agents/practice_designer_agent.py`.

### Practice Designer Agent implementation

```python
"""Create and configure the Practice Designer Agent."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL_NAME = os.getenv("MODEL_NAME")

if not MODEL_NAME:
    raise RuntimeError(
        "MODEL_NAME is not set. Add it to the project's .env file."
    )


practice_designer_agent = Agent(
    name="practice_designer_agent",
    model=LiteLlm(model=MODEL_NAME),
    description=(
        "Creates short beginner-friendly programming exercises from a topic "
        "and a previous explanation."
    ),
    instruction=(
        "You are a Practice Designer Agent.\n\n"
        "You will receive an original programming topic and an explanation "
        "created by another agent.\n\n"
        "Create one small, practical exercise that a beginner can complete "
        "in 10 to 20 minutes. Base it on the supplied topic and "
        "explanation.\n\n"
        "Do not rewrite or summarise the full explanation. Do not create a "
        "large application. Do not require external services.\n\n"
        "Return only this Markdown structure:\n\n"
        "## Practice Exercise\n"
        "Describe one clear and concrete task.\n\n"
        "### Expected Input\n"
        "State the expected input, or write `Not applicable.`\n\n"
        "### Expected Output\n"
        "State the expected output, or write `Not applicable.`\n\n"
        "### Hints\n"
        "Give one or two short hints without revealing the full solution."
    ),
)
```

### Agent responsibility

The agent has one narrow responsibility: generate a practical exercise from information that already exists.

It receives two pieces of context:

```text
Original topic
Previous explanation from the Explainer Agent
```

It returns:

```markdown
## Practice Exercise
A short practical task.

### Expected Input
The input required by the exercise, or `Not applicable.`

### Expected Output
The expected result, or `Not applicable.`

### Hints
One or two hints.
```

The agent is explicitly told not to reproduce the full explanation. It is also told to avoid large applications and external services, because the exercise should normally be achievable by a beginner in 10 to 20 minutes.

### Loading the project configuration

The Practice Designer Agent loads the same project-level `.env` file as the Explainer Agent:

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
```

Using an explicit project path makes the configuration independent of the directory from which the file is imported.

The model name is read safely:

```python
MODEL_NAME = os.getenv("MODEL_NAME")
```

If it is missing, the program raises a clear error:

```python
if not MODEL_NAME:
    raise RuntimeError(
        "MODEL_NAME is not set. Add it to the project's .env file."
    )
```

### Importing the Practice Designer Agent

`main.py` imports the new agent:

```python
from agents.practice_designer_agent import practice_designer_agent
```

The same reusable `run_agent()` function can execute either agent because it receives the agent object, prompt and session identifier as arguments:

```python
async def run_agent(agent, prompt: str, session_id: str) -> str:
    """Run one ADK agent and return its final text response."""
```

Separate session identifiers are used:

```text
explainer_session
practice_designer_session
```

This keeps the two runs distinct. The information needed by the second agent is passed explicitly in its prompt rather than relying on hidden conversation history.

### Passing the topic and explanation to the new agent

After the Explainer Agent returns its output, `main.py` builds the second prompt:

```python
practice_prompt = f"""Original topic:
{topic}

Explanation produced by the Explainer Agent:
{explanation}

Create one short beginner-friendly practice exercise based on this topic
and explanation.
"""
```

The Practice Designer Agent is then executed:

```python
practice = await run_agent(
    practice_designer_agent,
    practice_prompt,
    "practice_designer_session",
)
```

This hand-off satisfies the central Task 5 requirement. The second agent receives both the original topic and the previous agent's explanation.

### Replacing the draft exercise

The Explainer Agent still generates the complete eight-heading structure required by the validator. Its initial `Practice Exercise` section is treated as a placeholder.

The helper function in `main.py` replaces that section with the specialised agent's output:

```python
def replace_practice_section(
    study_guide: str,
    practice: str,
) -> str:
    """Replace the existing Practice Exercise section with agent output."""
    lines = study_guide.splitlines()
    target_heading = "## Practice Exercise"
    start_index = None
    end_index = len(lines)

    for index, line in enumerate(lines):
        if line.strip() == target_heading:
            start_index = index
            break

    if start_index is None:
        return study_guide

    for index in range(start_index + 1, len(lines)):
        if lines[index].strip().startswith("## "):
            end_index = index
            break

    practice_lines = practice.strip().splitlines()

    if (
        practice_lines
        and practice_lines[0].strip() == target_heading
    ):
        practice_lines = practice_lines[1:]

    combined_lines = (
        lines[:start_index + 1]
        + [""]
        + practice_lines
        + [""]
        + lines[end_index:]
    )

    return "\n".join(combined_lines).strip() + "\n"
```

The function first locates:

```markdown
## Practice Exercise
```

It then finds the next level-two heading, removes the content between the two headings and inserts the specialised exercise.

If the Practice Designer Agent also returns its own `## Practice Exercise` heading, that duplicate heading is removed before insertion. This preserves exactly one required heading in the final document.

### Complete Task 5 generation sequence

The relevant part of `main.py` now follows this order:

```python
explanation = await run_agent(
    explainer_agent,
    explainer_prompt,
    "explainer_session",
)

practice_prompt = f"""Original topic:
{topic}

Explanation produced by the Explainer Agent:
{explanation}

Create one short beginner-friendly practice exercise based on this topic
and explanation.
"""

practice = await run_agent(
    practice_designer_agent,
    practice_prompt,
    "practice_designer_session",
)

study_guide = replace_practice_section(
    explanation,
    practice,
)

validation_result = validate_required_sections(study_guide)
```

The file-writing tool receives `study_guide`, not the unmodified Explainer Agent output:

```python
save_result = save_markdown_file(
    str(OUTPUT_FILE),
    study_guide,
)
```

### Checking the Python files

Run all project commands from the project root:

```bash
cd ~/ai-agents-intro
source .venv/bin/activate
```

Check the relevant files for syntax errors:

```bash
python -m py_compile \
    agents/explainer_agent.py \
    agents/practice_designer_agent.py \
    tools/file_writer.py \
    tools/validation.py \
    main.py
```

No output means Python found no syntax errors.

### Testing the multi-agent workflow

Start Ollama in a separate WSL terminal:

```bash
ollama serve
```

In the project terminal, test the workflow with:

```bash
python main.py "Python list comprehensions"
```

Test another topic:

```bash
python main.py "Python dictionaries"
```

A successful run should finish with messages similar to:

```text
Validation passed: all required sections are present.
Markdown file saved successfully: /home/aleksandre/ai-agents-intro/output/study_guide.md
```

The exact absolute path may differ between systems.

### Checking the generated exercise

Display the exercise and the sections following it:

```bash
grep -A 20 '^## Practice Exercise' output/study_guide.md
```

A suitable result for `Python list comprehensions` could resemble:

````markdown
## Practice Exercise

Create a list called `numbers` containing the numbers from 1 to 5. Use a
list comprehension to create another list containing their squares.

### Expected Input

```python
numbers = [1, 2, 3, 4, 5]
```

### Expected Output

```text
[1, 4, 9, 16, 25]
```

### Hints

* Use a `for` clause inside square brackets.
* Multiply each number by itself or use `** 2`.
````

The exact wording may vary because the exercise is generated by the local model. The important requirements are that it is small, practical, connected to the topic and contains the requested input, output and hints.

### Task 5 validation

The following requirements have been implemented:

* [x] Created `agents/practice_designer_agent.py`
* [x] Gave the agent a clear and separate responsibility
* [x] Passed the original topic to the agent
* [x] Passed the Explainer Agent's output to the agent
* [x] Made the agent generate a practice exercise
* [x] Requested expected input when applicable
* [x] Requested expected output when applicable
* [x] Requested one or two hints
* [x] Instructed the agent not to rewrite the full explanation
* [x] Limited exercises to small beginner-friendly tasks
* [x] Connected the agent to the workflow in `main.py`
* [x] Replaced the draft exercise with the specialised agent's output
* [x] Kept deterministic validation before file writing

## Task 6: Reviewer Agent

> **Current implementation note:** Task 6 originally replaced the `Review Comments` placeholder in the draft. Task 7 now passes the assembled draft to the Reviewer Agent and then builds the final Markdown deterministically.

A generated study guide may contain all required headings while still having weak explanations, incomplete examples or unclear instructions. Task 6 adds a separate quality-control agent that examines the current draft and reports specific weaknesses.

The Reviewer Agent does not create a replacement study guide. Its responsibility is limited to reviewing the existing draft and producing short, actionable comments.

The Reviewer Agent is defined in:

```text
agents/reviewer_agent.py
```

### Reviewer Agent implementation

```python
"""Create and configure the Reviewer Agent."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL_NAME = os.getenv("MODEL_NAME")

if not MODEL_NAME:
    raise RuntimeError(
        "MODEL_NAME is not set. Add it to the project's .env file."
    )


reviewer_agent = Agent(
    name="reviewer_agent",
    model=LiteLlm(model=MODEL_NAME),
    description=(
        "Reviews draft programming study guides and provides short, "
        "actionable quality-control comments."
    ),
    instruction=(
        "You are a Reviewer Agent.\n\n"
        "You will receive an existing draft of a programming study guide.\n\n"
        "Review the draft for clarity, completeness, structure and "
        "usefulness for a beginner.\n\n"
        "Identify:\n"
        "- important information that is missing;\n"
        "- explanations that are ambiguous or unclear;\n"
        "- specific improvements that should be made;\n"
        "- whether the draft should be approved or revised.\n\n"
        "Be critical but constructive. Keep the review short and "
        "actionable.\n\n"
        "Do not rewrite the study guide. Do not create a replacement "
        "explanation, example or exercise. Comment only on the existing "
        "draft.\n\n"
        "Avoid vague comments such as `Improve the explanation`. Give "
        "specific comments such as `The example creates a function but "
        "does not show how to call it`.\n\n"
        "If a category has no meaningful problems, write "
        "`None identified.`\n\n"
        "Return only this Markdown structure:\n\n"
        "## Review Comments\n\n"
        "### Missing Information\n"
        "List missing information or write `None identified.`\n\n"
        "### Ambiguous or Unclear Explanations\n"
        "List unclear points or write `None identified.`\n\n"
        "### Suggestions for Improvement\n"
        "Give short and specific suggestions or write "
        "`No changes required.`\n\n"
        "### Recommendation\n"
        "Write a short approval or revision recommendation."
    ),
)
```

### Reviewer Agent responsibility

The agent receives the current study-guide draft after the specialised practice exercise has been inserted. It reviews that existing content for:

```text
Missing information
Ambiguous or unclear explanations
Specific suggestions for improvement
A short approval or revision recommendation
```

It returns only the following structure:

```markdown
## Review Comments

### Missing Information
Specific missing information, or `None identified.`

### Ambiguous or Unclear Explanations
Specific unclear points, or `None identified.`

### Suggestions for Improvement
Short actionable suggestions, or `No changes required.`

### Recommendation
A brief approval or revision recommendation.
```

The prompt explicitly prevents the agent from rewriting the explanation, example, exercise or complete guide. This keeps the Reviewer Agent separate from the Explainer Agent and Practice Designer Agent.

### Importing the Reviewer Agent

`main.py` imports the agent with:

```python
from agents.reviewer_agent import reviewer_agent
```

The existing reusable `run_agent()` function is also used for this agent. A separate session identifier keeps the run independent:

```text
reviewer_session
```

The draft itself is passed explicitly in the prompt. The Reviewer Agent therefore does not depend on hidden conversation history from the previous agents.

### Creating the reviewer prompt

The prompt includes the original topic and the current draft:

```python
def create_reviewer_prompt(
    topic: str,
    study_guide: str,
) -> str:
    """Create the prompt sent to the Reviewer Agent."""
    return f"""Original topic:

{topic}

Current draft study guide:

--- START OF DRAFT ---

{study_guide}

--- END OF DRAFT ---

Review this existing draft for clarity, completeness, structure and usefulness
for a beginner.

The current content under `## Review Comments` is only a placeholder. Ignore
that placeholder when reviewing the draft.

Return only the requested Review Comments Markdown section. Do not rewrite the
study guide.
"""
```

The start and end markers make it clearer which content is the draft being reviewed. The agent is also told to ignore the temporary content under `## Review Comments`, because that content exists only to preserve the required eight-heading structure before the review is inserted.

### General section-replacement helper

Task 5 used a helper dedicated to the Practice Exercise section. Task 6 replaces it with a reusable helper that can update either `## Practice Exercise` or `## Review Comments`.

The first helper extracts the body returned beneath the requested heading:

```python
def extract_section_body(
    generated_content: str,
    section_heading: str,
) -> list[str]:
    """Extract content beneath a generated level-two heading."""
    lines = generated_content.strip().splitlines()
    heading_index = None

    for index, line in enumerate(lines):
        if line.strip() == section_heading:
            heading_index = index
            break

    if heading_index is None:
        return lines

    section_lines = []

    for line in lines[heading_index + 1:]:
        if line.strip().startswith("## "):
            break

        section_lines.append(line)

    return section_lines
```

The general replacement helper locates the requested section in the study guide and replaces its current body:

```python
def replace_markdown_section(
    document: str,
    section_heading: str,
    generated_content: str,
) -> str:
    """Replace one level-two Markdown section with generated content."""
    lines = document.splitlines()
    start_index = None
    end_index = len(lines)

    for index, line in enumerate(lines):
        if line.strip() == section_heading:
            start_index = index
            break

    if start_index is None:
        return document

    for index in range(start_index + 1, len(lines)):
        if lines[index].strip().startswith("## "):
            end_index = index
            break

    section_body = extract_section_body(
        generated_content,
        section_heading,
    )

    while section_body and not section_body[0].strip():
        section_body.pop(0)

    while section_body and not section_body[-1].strip():
        section_body.pop()

    combined_lines = (
        lines[:start_index + 1]
        + [""]
        + section_body
        + [""]
        + lines[end_index:]
    )

    return "\n".join(combined_lines).strip() + "\n"
```

If an agent includes the requested level-two heading in its response, `extract_section_body()` removes that duplicate heading before insertion. If the agent returns only the section body, the complete response is inserted directly.

### Complete Task 6 generation sequence

The agents now run in this order:

```python
explanation = await run_agent(
    explainer_agent,
    create_explainer_prompt(topic),
    "explainer_session",
)

practice = await run_agent(
    practice_designer_agent,
    create_practice_prompt(topic, explanation),
    "practice_designer_session",
)

draft_with_practice = replace_markdown_section(
    explanation,
    "## Practice Exercise",
    practice,
)

review = await run_agent(
    reviewer_agent,
    create_reviewer_prompt(
        topic,
        draft_with_practice,
    ),
    "reviewer_session",
)

completed_guide = replace_markdown_section(
    draft_with_practice,
    "## Review Comments",
    review,
)
```

This order matters. The Reviewer Agent receives the current draft after the Practice Designer Agent has replaced the initial exercise. It can therefore review both the explanation and the final specialised exercise.

The completed guide is validated only after the review comments have been inserted:

```python
validation_result = validate_required_sections(study_guide)
```

The final Markdown file therefore contains the Reviewer Agent's comments rather than the original placeholder.

### Checking the Python files

Run all commands from the project root:

```bash
cd ~/ai-agents-intro
source .venv/bin/activate
```

Check the relevant files for syntax errors:

```bash
python -m py_compile \
    agents/explainer_agent.py \
    agents/practice_designer_agent.py \
    agents/reviewer_agent.py \
    tools/file_writer.py \
    tools/validation.py \
    main.py
```

No output means Python found no syntax errors.

### Testing the three-agent workflow

Start Ollama in a separate WSL terminal:

```bash
ollama serve
```

In the project terminal, run:

```bash
python main.py "Python list comprehensions"
```

Test another topic:

```bash
python main.py "Python functions"
```

A successful run should end with messages similar to:

```text
Validation passed: all required sections are present.
Markdown file saved successfully: /home/aleksandre/ai-agents-intro/output/study_guide.md
```

The exact absolute path may differ between systems.

### Checking the generated review

Display the review and the following section:

```bash
grep -A 30 '^## Review Comments' output/study_guide.md
```

A possible result could resemble:

```markdown
## Review Comments

### Missing Information

The guide does not explain when a normal loop may be clearer than a list
comprehension.

### Ambiguous or Unclear Explanations

The phrase "more efficient" is unclear because the guide does not state
whether it refers to readability or execution speed.

### Suggestions for Improvement

Clarify that a list comprehension is mainly a concise syntax and is not
necessarily faster in every situation.

### Recommendation

Revision recommended before final approval.
```

The exact wording may vary because the review is generated by the local model. The important requirements are that the comments are short, specific and focused on improving the existing draft rather than replacing it.

Check that the final file still contains every required level-two heading:

```bash
grep '^## ' output/study_guide.md
```

Expected result:

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

### Task 6 validation

The following requirements have been implemented:

* [x] Created `agents/reviewer_agent.py`
* [x] Made the agent review an existing draft
* [x] Made the agent identify missing information
* [x] Made the agent identify ambiguous or unclear explanations
* [x] Made the agent provide specific suggestions for improvement
* [x] Made the agent provide an approval or revision recommendation
* [x] Instructed the agent not to rewrite the complete guide
* [x] Passed the current study-guide draft to the agent
* [x] Ran the Reviewer Agent after the Practice Designer Agent
* [x] Replaced the temporary `Review Comments` content
* [x] Included the review comments in the final Markdown file
* [x] Kept deterministic validation before file writing

## Task 7: Sequential workflow

Task 7 connects the existing agents and deterministic tools into one readable pipeline. Each step receives the output it needs from the previous step, and `main.py` keeps agent execution separate from Markdown assembly, validation and file writing.

### Required execution order

```text
Topic input
    ↓
Explainer Agent
    ↓
Practice Designer Agent
    ↓
Draft Study Guide
    ↓
Reviewer Agent
    ↓
Final Markdown Assembly
    ↓
Validation Tool
    ↓
Save Markdown Tool
```

The Practice Designer Agent receives both the original topic and the Explainer Agent's output. The Reviewer Agent receives the assembled draft, including the specialised exercise. The final Markdown is built only after the review has been generated.

### Final Markdown structure

The generated file must contain these exact headings:

```markdown
# Topic

## Simple Explanation

## Key Concepts

## Example

## Practice Exercise

## Common Mistakes

## Review Comments

## Final Summary
```

`# Topic` is intentionally a level-one heading. The remaining required sections use level-two headings.

### Complete `main.py`

```python
"""Run the sequential AI study-guide workflow."""

import asyncio
import re
import sys
from pathlib import Path
from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.explainer_agent import explainer_agent
from agents.practice_designer_agent import practice_designer_agent
from agents.reviewer_agent import reviewer_agent
from tools.file_writer import save_markdown_file
from tools.validation import validate_required_sections


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = PROJECT_ROOT / "output" / "study_guide.md"

APP_NAME = "ai_study_guide_generator"
USER_ID = "student"


def get_topic_from_user() -> str:
    """Return a topic from command-line arguments or interactive input."""
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:]).strip()
    else:
        topic = input("Enter a programming topic: ").strip()

    if not topic:
        raise ValueError("A programming topic is required.")

    return topic


async def run_agent(
    agent: Any,
    prompt: str,
    session_id: str,
) -> str:
    """Run one ADK agent and return its final text response."""
    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_response = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=message,
    ):
        if not event.is_final_response():
            continue

        if not event.content or not event.content.parts:
            continue

        response_parts = []

        for part in event.content.parts:
            text = getattr(part, "text", None)

            if text:
                response_parts.append(text)

        final_response = "".join(response_parts).strip()

    if not final_response:
        raise RuntimeError(
            f"{agent.name} did not return a final text response."
        )

    return final_response


def create_explainer_prompt(topic: str) -> str:
    """Create the prompt sent to the Explainer Agent."""
    return f"""Explain this programming topic for a beginner:

{topic}

Return these exact Markdown sections:

## Simple Explanation

Give a short and clear beginner-friendly explanation.

## Key Concepts

Describe the most important concepts.

## Example

Give one small practical example. Close every Markdown code block with
three backticks.

## Common Mistakes

Describe common beginner mistakes.

## Final Summary

Give a short summary of the topic.

Do not generate the Practice Exercise or Review Comments sections. Other
agents are responsible for those sections.
"""


def create_practice_prompt(
    topic: str,
    explanation: str,
) -> str:
    """Create the prompt sent to the Practice Designer Agent."""
    return f"""Original topic:

{topic}

Explanation produced by the Explainer Agent:

--- START OF EXPLANATION ---

{explanation}

--- END OF EXPLANATION ---

Create one small beginner-friendly practice exercise based on the topic and
the explanation.

Return only this Markdown structure:

## Practice Exercise

Describe one clear and practical exercise.

### Expected Input

State the expected input, or write `Not applicable.`

### Expected Output

State the expected output, or write `Not applicable.`

### Hints

Give one or two short hints.

Close every Markdown code block with three backticks.

Do not rewrite the explanation.
"""


def create_reviewer_prompt(
    topic: str,
    draft: str,
) -> str:
    """Create the prompt sent to the Reviewer Agent."""
    return f"""Original topic:

{topic}

Current draft study guide:

--- START OF DRAFT ---

{draft}

--- END OF DRAFT ---

Review the existing draft for clarity, completeness, structure and usefulness
for a beginner.

The current Review Comments content is only a placeholder. Ignore it while
reviewing.

Return only this Markdown structure:

## Review Comments

### Missing Information

Identify important missing information, or write `None identified.`

### Ambiguous or Unclear Explanations

Identify unclear explanations, or write `None identified.`

### Suggestions for Improvement

Give short and specific suggestions, or write `No changes required.`

### Recommendation

Give a short approval or revision recommendation.

Do not rewrite the study guide.
"""


def find_markdown_headings(
    lines: list[str],
) -> list[tuple[int, int, str]]:
    """Return Markdown headings outside fenced code blocks."""
    headings = []
    active_fence = None

    for index, line in enumerate(lines):
        stripped_line = line.strip()

        if stripped_line.startswith("```"):
            if active_fence == "```":
                active_fence = None
            elif active_fence is None:
                active_fence = "```"

            continue

        if stripped_line.startswith("~~~"):
            if active_fence == "~~~":
                active_fence = None
            elif active_fence is None:
                active_fence = "~~~"

            continue

        if active_fence is not None:
            continue

        match = re.match(
            r"^(#{1,6})\s+(.+?)\s*$",
            stripped_line,
        )

        if match:
            level = len(match.group(1))
            title = match.group(2).strip()

            headings.append(
                (
                    index,
                    level,
                    title,
                )
            )

    return headings


def extract_named_section(
    markdown: str,
    section_name: str,
) -> str:
    """Extract a named Markdown section regardless of heading level."""
    lines = markdown.strip().splitlines()
    headings = find_markdown_headings(lines)

    for position, heading in enumerate(headings):
        start_index, start_level, title = heading

        if title.casefold() != section_name.casefold():
            continue

        end_index = len(lines)

        for next_heading in headings[position + 1:]:
            next_index, next_level, _ = next_heading

            if next_level <= start_level:
                end_index = next_index
                break

        return "\n".join(
            lines[start_index + 1:end_index]
        ).strip()

    return ""


def close_unmatched_code_fence(content: str) -> str:
    """Close an unmatched Markdown code fence in generated content."""
    lines = content.strip().splitlines()
    active_fence = None

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.startswith("```"):
            if active_fence == "```":
                active_fence = None
            elif active_fence is None:
                active_fence = "```"

        elif stripped_line.startswith("~~~"):
            if active_fence == "~~~":
                active_fence = None
            elif active_fence is None:
                active_fence = "~~~"

    cleaned_content = "\n".join(lines).strip()

    if active_fence is not None:
        cleaned_content = (
            f"{cleaned_content}\n{active_fence}"
        )

    return cleaned_content


def get_agent_section(
    generated_content: str,
    section_name: str,
) -> str:
    """Extract an agent section or use its complete response."""
    section_body = extract_named_section(
        generated_content,
        section_name,
    )

    if not section_body:
        section_body = generated_content.strip()

    return close_unmatched_code_fence(section_body)


def add_section(
    document_parts: list[str],
    heading: str,
    body: str,
    fallback: str,
) -> None:
    """Append one required Markdown section."""
    cleaned_body = close_unmatched_code_fence(
        body.strip()
    )

    if not cleaned_body:
        cleaned_body = fallback

    document_parts.extend(
        [
            heading,
            "",
            cleaned_body,
            "",
        ]
    )


def assemble_markdown(
    topic: str,
    explanation: str,
    practice: str,
    review: str | None = None,
) -> str:
    """Assemble the draft or final Markdown study guide."""
    simple_explanation = extract_named_section(
        explanation,
        "Simple Explanation",
    )

    key_concepts = extract_named_section(
        explanation,
        "Key Concepts",
    )

    example = extract_named_section(
        explanation,
        "Example",
    )

    common_mistakes = extract_named_section(
        explanation,
        "Common Mistakes",
    )

    final_summary = extract_named_section(
        explanation,
        "Final Summary",
    )

    practice_body = get_agent_section(
        practice,
        "Practice Exercise",
    )

    if review is None:
        review_body = (
            "The Reviewer Agent has not reviewed the draft yet."
        )
    else:
        review_body = get_agent_section(
            review,
            "Review Comments",
        )

    document_parts = [
        "# Topic",
        "",
        topic,
        "",
    ]

    add_section(
        document_parts,
        "## Simple Explanation",
        simple_explanation,
        "No simple explanation was generated.",
    )

    add_section(
        document_parts,
        "## Key Concepts",
        key_concepts,
        "No key concepts were generated.",
    )

    add_section(
        document_parts,
        "## Example",
        example,
        "No example was generated.",
    )

    add_section(
        document_parts,
        "## Practice Exercise",
        practice_body,
        "No practice exercise was generated.",
    )

    add_section(
        document_parts,
        "## Common Mistakes",
        common_mistakes,
        "No common mistakes were generated.",
    )

    add_section(
        document_parts,
        "## Review Comments",
        review_body,
        "No review comments were generated.",
    )

    add_section(
        document_parts,
        "## Final Summary",
        final_summary,
        "No final summary was generated.",
    )

    return "\n".join(document_parts).strip() + "\n"


async def run_workflow(topic: str) -> int:
    """Run the complete sequential study-guide workflow."""
    print(f"Topic: {topic}")

    print("\n[1/7] Running Explainer Agent...")

    explanation = await run_agent(
        explainer_agent,
        create_explainer_prompt(topic),
        "explainer_session",
    )

    print("Explainer Agent completed.")

    print("\n[2/7] Running Practice Designer Agent...")

    practice = await run_agent(
        practice_designer_agent,
        create_practice_prompt(
            topic,
            explanation,
        ),
        "practice_designer_session",
    )

    print("Practice Designer Agent completed.")

    print("\n[3/7] Assembling the draft study guide...")

    draft = assemble_markdown(
        topic=topic,
        explanation=explanation,
        practice=practice,
    )

    print("Draft study guide assembled.")

    print("\n[4/7] Running Reviewer Agent...")

    review = await run_agent(
        reviewer_agent,
        create_reviewer_prompt(
            topic,
            draft,
        ),
        "reviewer_session",
    )

    print("Reviewer Agent completed.")

    print("\n[5/7] Assembling the final Markdown...")

    final_markdown = assemble_markdown(
        topic=topic,
        explanation=explanation,
        practice=practice,
        review=review,
    )

    print("Final Markdown assembled.")

    print("\n[6/7] Validating required sections...")

    validation_result = validate_required_sections(
        final_markdown
    )

    if not validation_result["valid"]:
        print("Validation failed.")
        print("Missing sections:")

        for section in validation_result["missing_sections"]:
            print(f"- {section}")

        print("\nGenerated Markdown for debugging:")
        print("--------------------------------")
        print(final_markdown)
        print("--------------------------------")
        print("The Markdown file was not saved.")

        return 1

    print(
        "Validation passed: all required sections are present."
    )

    print("\n[7/7] Saving the Markdown file...")

    save_result = save_markdown_file(
        str(OUTPUT_FILE),
        final_markdown,
    )

    print(save_result)

    if save_result.startswith(
        "Could not save Markdown file:"
    ):
        return 1

    print("\nWorkflow completed successfully.")
    print(f"Final file: {OUTPUT_FILE}")

    return 0


def main() -> None:
    """Read the topic and run the asynchronous workflow."""
    try:
        topic = get_topic_from_user()
        exit_code = asyncio.run(
            run_workflow(topic)
        )
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}")
        exit_code = 1
    except KeyboardInterrupt:
        print("\nWorkflow cancelled.")
        exit_code = 130

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()

```

### Updated validation tool

Task 7 updates the validator because the final document now uses `# Topic` rather than `## Topic`. The validator also ignores apparent headings inside fenced code blocks.

Replace `tools/validation.py` with:

```python
"""Utilities for validating generated Markdown study guides."""


REQUIRED_HEADINGS = [
    "# Topic",
    "## Simple Explanation",
    "## Key Concepts",
    "## Example",
    "## Practice Exercise",
    "## Common Mistakes",
    "## Review Comments",
    "## Final Summary",
]


def validate_required_sections(markdown: str) -> dict:
    """Check whether Markdown contains every required heading."""
    headings = set()
    active_fence = None

    for line in markdown.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith("```"):
            if active_fence == "```":
                active_fence = None
            else:
                active_fence = "```"

            continue

        if stripped_line.startswith("~~~"):
            if active_fence == "~~~":
                active_fence = None
            else:
                active_fence = "~~~"

            continue

        if (
            active_fence is None
            and stripped_line.startswith("#")
        ):
            headings.add(stripped_line)

    missing_sections = [
        heading
        for heading in REQUIRED_HEADINGS
        if heading not in headings
    ]

    return {
        "valid": not missing_sections,
        "missing_sections": missing_sections,
    }

```

### Why Markdown is assembled in ordinary Python

The agents generate flexible content, but they are not trusted to control the final document structure. `assemble_markdown()` creates every required heading in a fixed order. This makes the workflow easier to inspect and prevents an agent from accidentally omitting, renaming or reordering the final sections.

The Explainer Agent provides content for:

```text
Simple Explanation
Key Concepts
Example
Common Mistakes
Final Summary
```

The Practice Designer Agent provides:

```text
Practice Exercise
```

The Reviewer Agent provides:

```text
Review Comments
```

`main.py` then combines those results.

### Progress messages

The workflow prints one message for each stage:

```text
[1/7] Running Explainer Agent...
[2/7] Running Practice Designer Agent...
[3/7] Assembling the draft study guide...
[4/7] Running Reviewer Agent...
[5/7] Assembling the final Markdown...
[6/7] Validating required sections...
[7/7] Saving the Markdown file...
```

These messages make the execution order visible and make failures easier to locate.

### Validation failure encountered

The first Task 7 run reached validation but reported:

```text
Validation failed.
Missing sections:
- ## Practice Exercise
- ## Common Mistakes
- ## Review Comments
- ## Final Summary
The Markdown file was not saved.
```

All three agents had completed, so the failure was not caused by an agent failing to run. The pattern indicated that generated Markdown probably contained an unclosed fenced code block in or before the `Example` section. A Markdown parser then treated later headings as code rather than document headings.

The final `main.py` therefore includes:

```python
def close_unmatched_code_fence(content: str) -> str:
```

This function detects an unmatched triple-backtick or triple-tilde fence and closes it before the next assembled section is added. The prompts also explicitly tell the agents to close every Markdown code block.

The validator remains strict: headings inside a genuine fenced code block do not count as required document sections.

### Checking the Python files

Run commands from the project root:

```bash
cd ~/ai-agents-intro
source .venv/bin/activate
```

Check the complete project for syntax errors:

```bash
python -m py_compile \
    agents/explainer_agent.py \
    agents/practice_designer_agent.py \
    agents/reviewer_agent.py \
    tools/file_writer.py \
    tools/validation.py \
    main.py
```

No output means Python found no syntax errors.

### Running the complete workflow

Start Ollama in a separate WSL terminal:

```bash
ollama serve
```

In the project terminal, run:

```bash
python main.py "Python list comprehensions"
```

The topic can also be entered interactively:

```bash
python main.py
```

Expected prompt:

```text
Enter a programming topic:
```

### Expected successful result

A successful run should end with output similar to:

```text
[6/7] Validating required sections...
Validation passed: all required sections are present.

[7/7] Saving the Markdown file...
Markdown file saved successfully: /home/aleksandre/ai-agents-intro/output/study_guide.md

Workflow completed successfully.
Final file: /home/aleksandre/ai-agents-intro/output/study_guide.md
```

The exact absolute path may differ between systems.

### Inspecting the generated file

Display the file:

```bash
cat output/study_guide.md
```

Display every Markdown heading:

```bash
grep '^#' output/study_guide.md
```

Expected required headings:

```text
# Topic
## Simple Explanation
## Key Concepts
## Example
## Practice Exercise
## Common Mistakes
## Review Comments
## Final Summary
```

Additional level-three headings such as `### Expected Input`, `### Hints` or `### Recommendation` may also appear.

### Task 7 validation

The following requirements have been implemented:

* [x] `main.py` runs the complete workflow.
* [x] The topic is received from a command-line argument or interactive input.
* [x] The Explainer Agent runs first.
* [x] The Practice Designer Agent receives the topic and Explainer Agent output.
* [x] Python assembles a draft study guide.
* [x] The Reviewer Agent receives and reviews the assembled draft.
* [x] Python assembles the final Markdown in one place.
* [x] The final Markdown contains all required headings.
* [x] The validation tool runs before the file is saved.
* [x] Missing headings are reported individually.
* [x] Invalid Markdown is not saved.
* [x] Valid Markdown is saved to `output/study_guide.md`.
* [x] Useful progress messages show the execution order.
* [x] Unmatched generated code fences are repaired before final assembly.


## Task 8: Basic error handling and configuration

Task 8 handles common expected failures before or during the workflow without replacing every exception with an unhelpful generic message.

The project now checks:

* whether the topic is empty;
* whether required environment variables are present and valid;
* whether the Ollama server is reachable;
* whether the configured Ollama model is installed;
* whether the final Markdown contains every required heading;
* whether the generated file can be written successfully.

Unexpected programming errors are not caught by a blanket `except Exception` block. They still produce their normal traceback during development.

### New configuration module

The new file is:

```text
config.py
```

It loads the project-level `.env` file, validates the model provider, checks the LiteLLM model prefix and validates the Ollama URL. It returns one immutable `Settings` object used by `main.py`.

Required variables:

```env
MODEL_PROVIDER=ollama
MODEL_NAME=ollama_chat/llama3.2:3b
OLLAMA_API_BASE=http://localhost:11434
```

When a value is missing, the program reports the exact variable names and explains that `.env.example` should be copied to `.env`.

Example:

```text
Configuration error: Missing required environment variable(s): MODEL_NAME. Copy `.env.example` to `.env` and fill in the required values.
```

### Ollama preflight tool

The new file is:

```text
tools/ollama.py
```

Before any agent runs, it requests:

```text
http://localhost:11434/api/tags
```

This confirms both that the server is reachable and that the configured local model exists.

When Ollama is not running, the program reports:

```text
Ollama connection error: Could not connect to Ollama at http://localhost:11434: ... Start it with `ollama serve`.
```

When Ollama is running but the model is absent, the program reports:

```text
Model error: Ollama is running, but model "llama3.2:3b" is not available.
Install it with: ollama pull llama3.2:3b
Available models: ...
```

### Empty topic handling

Input is checked before configuration or agent execution.

```bash
python main.py "   "
```

Expected result:

```text
Input error: Topic cannot be empty. Example: `python main.py "Python list comprehensions"`.
```

The interactive form is also checked:

```bash
python main.py
```

Pressing Enter without a topic produces the same clear input error.

### File-writing errors

`tools/file_writer.py` now raises a specific `FileWriteError` while preserving the original `OSError` as its cause.

`main.py` handles this expected error and reports the attempted path plus the operating-system message:

```text
File-writing error: Could not save Markdown file to `...`: ...
Check the output path, directory permissions and available disk space.
```

The file writer still creates missing parent directories automatically and returns the absolute path after a successful write.

### Validation failures

Validation still happens before file writing. When headings are missing, the program prints each missing heading, displays the generated Markdown for debugging and explicitly states that the file was not saved.

Example:

```text
Validation failed: the final Markdown is missing required headings.
Missing headings:
- ## Review Comments
- ## Final Summary
...
The Markdown file was not saved.
```

### New execution order

The progress messages now expose all nine stages:

```text
[1/9] Checking configuration...
[2/9] Checking Ollama server and model...
[3/9] Running Explainer Agent...
[4/9] Running Practice Designer Agent...
[5/9] Assembling the draft study guide...
[6/9] Running Reviewer Agent...
[7/9] Assembling the final Markdown...
[8/9] Validating required sections...
[9/9] Saving the Markdown file...
```

### Replacing the project files

Task 8 adds or replaces these complete files:

```text
config.py
main.py
agents/explainer_agent.py
agents/practice_designer_agent.py
agents/reviewer_agent.py
tools/file_writer.py
tools/ollama.py
tools/validation.py
.env.example
.gitignore
```

The agent modules now expose factory functions instead of reading environment variables at import time:

```python
create_explainer_agent(model_name)
create_practice_designer_agent(model_name)
create_reviewer_agent(model_name)
```

This matters because `main.py` can validate configuration and Ollama first. An invalid `.env` no longer causes an obscure import-time failure before the program can print a useful message.

### Checking syntax

Run this from the project root:

```bash
python -m py_compile \
    config.py \
    main.py \
    agents/explainer_agent.py \
    agents/practice_designer_agent.py \
    agents/reviewer_agent.py \
    tools/file_writer.py \
    tools/ollama.py \
    tools/validation.py
```

No output means Python found no syntax errors.

### Testing the successful workflow

Start Ollama in a separate WSL terminal:

```bash
ollama serve
```

In the project terminal:

```bash
cd ~/ai-agents-intro
source .venv/bin/activate
python main.py "Python list comprehensions"
```

A successful run should reach:

```text
Validation passed: all required sections are present.
Markdown file saved successfully: .../output/study_guide.md
Workflow completed successfully.
```

## Troubleshooting

### `Configuration error: Missing required environment variable(s)`

Create the local configuration file:

```bash
cp .env.example .env
```

Then confirm that `.env` contains:

```env
MODEL_PROVIDER=ollama
MODEL_NAME=ollama_chat/llama3.2:3b
OLLAMA_API_BASE=http://localhost:11434
```

Do not commit `.env`. Confirm that Git ignores it:

```bash
git check-ignore .env
```

Expected output:

```text
.env
```

### `Unsupported MODEL_PROVIDER`

The current project supports:

```env
MODEL_PROVIDER=ollama
```

Changing it to another provider is not enough by itself. The project would also need provider-specific environment variables and a corresponding preflight check.

### `MODEL_NAME must use a LiteLLM Ollama prefix`

Use a complete LiteLLM model identifier:

```env
MODEL_NAME=ollama_chat/llama3.2:3b
```

Do not use only:

```env
MODEL_NAME=llama3.2:3b
```

### `Could not connect to Ollama`

Start the server in a separate terminal:

```bash
ollama serve
```

Keep that terminal open. Test the server directly:

```bash
curl http://localhost:11434/api/tags
```

If `.env` uses another host or port, confirm that `OLLAMA_API_BASE` matches the real server address.

### `Model ... is not available`

Install the configured model:

```bash
ollama pull llama3.2:3b
```

Then verify it:

```bash
ollama list
ollama show llama3.2:3b
```

The name after the LiteLLM prefix in `MODEL_NAME` must match an installed Ollama model.

### `Topic cannot be empty`

Pass a non-empty topic:

```bash
python main.py "Python dictionaries"
```

Topics containing spaces should be enclosed in quotation marks.

### `File-writing error`

Check:

* that the project directory is writable;
* that `output/` is not owned by another user;
* that enough disk space is available;
* that `output/study_guide.md` is not being blocked by unusual permissions.

Inspect permissions with:

```bash
ls -ld . output
ls -l output/study_guide.md
```

A normal repair for a user-owned project is:

```bash
mkdir -p output
chmod u+rwx output
```

Do not use broad permissions such as `chmod 777` as a routine fix.

### `Validation failed`

Read the listed missing headings and the generated Markdown printed below them. The invalid document is deliberately not saved.

Confirm that `tools/validation.py` requires:

```text
# Topic
## Simple Explanation
## Key Concepts
## Example
## Practice Exercise
## Common Mistakes
## Review Comments
## Final Summary
```

Also check for an unclosed Markdown code fence before a missing heading. `main.py` repairs ordinary unmatched triple-backtick and triple-tilde fences, but malformed generated Markdown may still require inspection.

### `ModuleNotFoundError` for `agents`, `tools` or `config`

Run project commands from the project root:

```bash
cd ~/ai-agents-intro
source .venv/bin/activate
```

Do not run package-level tests from inside `agents/` or `tools/`.

### Task 8 validation

The following requirements have been implemented:

* [x] The project checks for empty topic input.
* [x] The project validates required environment variables.
* [x] The project explains how to configure the model provider.
* [x] The project checks whether Ollama is running.
* [x] The project checks whether the configured model is installed.
* [x] The project handles file-writing errors with a specific exception.
* [x] The project reports validation failures and missing headings clearly.
* [x] Invalid Markdown is not saved.
* [x] The README contains troubleshooting notes and failure examples.
* [x] `.env.example` contains only safe example configuration.
* [x] `.env` remains excluded through `.gitignore`.
* [x] The project does not expose secrets.

## Current limitations

The validator checks document structure, not factual accuracy or teaching quality. It confirms that the required headings exist outside fenced code blocks, but it cannot prove that each explanation is correct, complete or appropriate for every learner.

The Reviewer Agent adds a quality-control step, but its comments are still generated by a language model. It may miss a problem, overstate a minor weakness or recommend an unnecessary change.

The preflight check confirms that Ollama and the selected model are available before generation starts. Ollama can still stop after that check, in which case the underlying agent exception remains visible for debugging.

The local `llama3.2:3b` model may vary between runs. It can produce different wording, malformed Markdown or incomplete content. The deterministic assembly logic protects the required final structure, closes unmatched code fences and uses fallback text when a section body is missing, but it does not automatically repair every possible content-quality problem.

Fallback text keeps the final document structurally valid, but a structurally valid guide may still require human revision. The workflow deliberately reports reviewer comments rather than attempting to rewrite every criticised section automatically.

The final responsibility split is:

```text
Configuration module    → environment validation
Ollama preflight tool     → server and model availability checks
Explainer Agent           → explanatory content
Practice Designer Agent   → beginner-friendly exercise
Reviewer Agent            → quality-control comments
Python orchestration      → explicit sequential hand-offs
Markdown assembly         → fixed final structure and order
Validation tool           → deterministic heading checks
File-writing tool         → deterministic file-system operation
```

Task 8 adds clear handling for expected input, configuration, Ollama, model, validation and file-system failures without hiding unexpected development errors.
