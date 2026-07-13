# AI Study Guide Generator

A Python project that uses several local AI agents to generate structured programming study guides.

The project uses Google ADK to define and organise agents, LiteLLM to connect the agents to a language model, and Ollama to run the model locally.

## Current status

Task 0 is complete. The initial project structure and starter files have been created.

Task 1 is complete. The Python environment, dependencies, Ollama server and local model have been configured and tested.

Task 2 is complete. The first agent, the Explainer Agent, has been created and tested with programming topics.

Task 3 is complete. A deterministic file-writing tool has been implemented, tested independently and connected to the project workflow.

Task 4 is complete. A deterministic validation tool now checks generated Markdown for eight required sections before the file-writing tool is allowed to save it. Invalid output is rejected and the missing sections are reported.

Task 5 is complete. A separate Practice Designer Agent now receives the original topic and the Explainer Agent's output, then creates a short beginner-friendly exercise with expected input, expected output and one or two hints.

Task 6 is complete. A Reviewer Agent now inspects the combined draft, identifies missing or unclear information, gives specific improvement suggestions and adds a short approval or revision recommendation to the final Markdown file.

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

## Current project workflow

The application currently:

1. Receives a programming topic.
2. Sends the topic to the Explainer Agent.
3. Generates a structured draft containing the eight required Markdown sections.
4. Sends the original topic and the Explainer Agent's output to the Practice Designer Agent.
5. Generates a small beginner-friendly exercise with expected input, expected output and hints.
6. Replaces the draft `Practice Exercise` section with the specialised exercise.
7. Sends the combined draft to the Reviewer Agent.
8. Generates short comments about missing information, unclear explanations and possible improvements.
9. Replaces the `Review Comments` placeholder with the Reviewer Agent's comments.
10. Validates the eight required Markdown headings.
11. Saves valid output in `output/study_guide.md`.

The Explainer Agent, Practice Designer Agent, Reviewer Agent, validation tool and Markdown file-writing tool have now been implemented. Each agent has a separate responsibility, while ordinary Python code controls the hand-offs, section replacement, validation and file writing.

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

## Current limitations

The Explainer Agent, Practice Designer Agent, Reviewer Agent, Markdown file-writing tool and validation tool have been implemented.

The validator checks structure only. It does not determine whether the explanation is factually correct, whether the example is ideal, whether the exercise has exactly the right difficulty or whether every reviewer comment is justified.

The Reviewer Agent improves quality control but remains a language-model component. Its comments are advisory rather than deterministic. It may overlook a weakness, report a minor issue as important or recommend a change that is unnecessary.

Because `llama3.2:3b` is a small local model, wording and formatting may vary between runs. The model may occasionally rename headings, use the wrong heading level or omit requested content. The validator catches missing required level-two headings, but it does not validate the Practice Designer Agent's or Reviewer Agent's level-three subsections individually.

The current design separates responsibilities:

```text
Explainer Agent          → explanation and initial structured draft
Practice Designer Agent  → focused beginner exercise
Reviewer Agent           → short quality-control comments
Python orchestration     → explicit hand-offs and section replacement
Python validator         → predictable structural checking
File-writing tool        → predictable file-system operation
```

Task 6 extends the multi-agent design without allowing every agent to solve the complete task again. Each agent receives the responsibility and context it needs, while deterministic Python code controls the workflow, combines the results, validates the final structure and saves the file.
