# AI Agents in Python

## Description

This project is a local multi-agent Python application that generates a structured programming study guide from a topic supplied by the user.

It uses three specialised AI agents:

- an Explainer Agent to explain the topic;
- a Practice Designer Agent to create a beginner-friendly exercise;
- a Reviewer Agent to review the assembled draft.

Ordinary Python code controls the order of execution, assembles the final Markdown document, validates its required headings and saves it to disk.

The project uses:

- Google ADK to define and run the agents;
- LiteLLM to connect the agents to the selected model;
- Ollama to run the model locally;
- `llama3.2:3b` as the local language model.

The workflow is sequential. Each stage depends on results produced earlier:

```text
Topic input
    ↓
Configuration and Ollama checks
    ↓
Explainer Agent
    ↓
Practice Designer Agent
    ↓
Draft assembly
    ↓
Reviewer Agent
    ↓
Final Markdown assembly
    ↓
Validation
    ↓
File writing
    ↓
output/study_guide.md
```

## Requirements

The project requires:

- Python 3.10 or later;
- a Python virtual environment;
- Ollama;
- the local `llama3.2:3b` model;
- the Python packages listed in `requirements.txt`.

The required Python packages are:

```text
google-adk
litellm
python-dotenv
```

The project was developed in Windows 11 with WSL2 and Ubuntu. Ollama was run inside WSL.

A dedicated GPU is not required, but local model speed depends on the computer's CPU, available memory and other running programs. The 3-billion-parameter model was selected because it requires fewer resources than larger models. CPU-only generation can still be slow.

## Setup

Run project commands from the project root:

```bash
cd ~/ai-agents-intro
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Upgrade `pip` and install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install Ollama in WSL:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

If installation reports that `zstd` is missing, install it first:

```bash
sudo apt update
sudo apt install zstd -y
```

Download the selected local model:

```bash
ollama pull llama3.2:3b
```

Confirm that it is installed:

```bash
ollama list
```

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

The `.env` file must contain:

```env
MODEL_PROVIDER=ollama
MODEL_NAME=ollama_chat/llama3.2:3b
OLLAMA_API_BASE=http://localhost:11434
```

The variables have the following roles:

- `MODEL_PROVIDER` selects the supported model provider. This project currently supports `ollama`.
- `MODEL_NAME` is the LiteLLM model identifier. The `ollama_chat/` prefix tells LiteLLM to use Ollama's chat interface.
- `OLLAMA_API_BASE` is the address of the local Ollama server.

The real `.env` file must not be committed. It is excluded through `.gitignore` because environment files may contain private configuration in other deployments.

The safe `.env.example` file can be committed because it contains example values rather than secrets.

Check that Git ignores the local environment file:

```bash
git check-ignore .env
```

Expected output:

```text
.env
```

This local Ollama configuration does not require an external API key. Do not place real API keys in the README or commit them to the repository.

## How to Run

Ollama must be running before the agents can use the model.

Open one WSL terminal and start the Ollama server:

```bash
ollama serve
```

Keep that terminal open.

Open a second WSL terminal, enter the project directory and activate the virtual environment:

```bash
cd ~/ai-agents-intro
source .venv/bin/activate
```

Run the project with a topic as a command-line argument:

```bash
python main.py "Python list comprehensions"
```

A topic containing spaces should be placed inside quotation marks.

The topic can also be entered interactively:

```bash
python main.py
```

The program then displays:

```text
Enter a programming topic:
```

Before running the agents, the application checks:

- that the topic is not empty;
- that all required environment variables exist;
- that the model provider is supported;
- that Ollama is reachable;
- that the configured model is installed.

After generation, it checks the required Markdown structure before saving the result.

A successful run creates or replaces:

```text
output/study_guide.md
```

Check the complete Python project for syntax errors with:

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

No output means that Python found no syntax errors.

## Example Input

Command:

```bash
python main.py "Python list comprehensions"
```

Topic received by the workflow:

```text
Python list comprehensions
```

## Example Output

The terminal output is similar to:

```text
[1/9] Checking configuration...
Configuration loaded: provider=ollama, model=ollama_chat/llama3.2:3b

[2/9] Checking Ollama server and model...
Ollama is available and model `llama3.2:3b` is installed.

Topic: Python list comprehensions

[3/9] Running Explainer Agent...
Explainer Agent completed.

[4/9] Running Practice Designer Agent...
Practice Designer Agent completed.

[5/9] Assembling the draft study guide...
Draft study guide assembled.

[6/9] Running Reviewer Agent...
Reviewer Agent completed.

[7/9] Assembling the final Markdown...
Final Markdown assembled.

[8/9] Validating required sections...
Validation passed: all required sections are present.

[9/9] Saving the Markdown file...
Markdown file saved successfully: .../output/study_guide.md

Workflow completed successfully.
```

The generated file follows this structure:

```markdown
# Topic

Python list comprehensions

## Simple Explanation

A list comprehension is a compact way to build a new list from an iterable.

## Key Concepts

Expression, iteration and optional filtering.

## Example

A small Python example.

## Practice Exercise

A beginner-friendly exercise with expected input, output and hints.

## Common Mistakes

Common syntax and readability mistakes.

## Review Comments

Short comments on missing, unclear or improvable parts.

## Final Summary

A brief summary of the topic.
```

The exact wording varies because it is generated by a language model.

## Project Structure

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
├── .gitignore
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

`main.py` controls the sequential workflow and the hand-offs between stages.

`config.py` loads and validates the environment configuration before the agents are created.

The `agents/` directory contains the specialised AI agents.

The `tools/` directory contains deterministic Python operations used for preflight checks, validation and file writing.

The `output/` directory contains the generated Markdown study guide.

## Agents

### Explainer Agent

The Explainer Agent receives the original programming topic and generates:

- a simple explanation;
- key concepts;
- a small example;
- common mistakes;
- a final summary.

It does not create the practice exercise or review comments. Those responsibilities belong to the other agents.

### Practice Designer Agent

The Practice Designer Agent receives:

- the original topic;
- the explanation generated by the Explainer Agent.

It creates one small exercise suitable for a beginner. The exercise includes expected input, expected output and one or two hints where applicable.

It does not rewrite the explanation.

### Reviewer Agent

The Reviewer Agent receives the assembled draft containing the explanation and practice exercise.

It examines the draft for:

- missing information;
- ambiguous or unclear explanations;
- possible improvements;
- an approval or revision recommendation.

It comments on the existing draft rather than generating a replacement study guide.

## Tools

### Configuration loader

`config.py` loads `.env`, checks the required environment variables and validates the configured provider, model name and Ollama server URL.

It reports missing or invalid configuration before agent execution begins.

### Ollama preflight tool

`tools/ollama.py` contacts Ollama's local `/api/tags` endpoint.

It confirms:

- that the Ollama server is running;
- that the server returns a readable response;
- that the configured local model is installed.

A stopped server and a missing model produce different error messages so that the user knows which problem to fix.

### Validation tool

`tools/validation.py` checks that the final Markdown contains these exact required headings:

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

The validator ignores text inside fenced code blocks. If headings are missing, the program lists them and does not save the invalid document.

### File-writing tool

`tools/file_writer.py` creates missing parent directories and writes the final Markdown to disk using UTF-8 encoding.

It raises a clear file-writing error if the path cannot be created or written, for example because of permissions, an invalid path or insufficient disk space.

### Markdown assembly functions

The helper functions in `main.py` extract the relevant generated sections, close unmatched code fences, insert fallback content when necessary and assemble the required headings in a fixed order.

These are deterministic Python operations rather than model-generated decisions.

## Self-Validation Checklist

- [x] README.md includes all required sections.
- [x] README.md explains the purpose and workflow of the project.
- [x] README.md explains how to install the Python dependencies.
- [x] README.md explains how to install and start Ollama.
- [x] README.md explains how to download the selected model.
- [x] README.md explains how to configure the model provider.
- [x] README.md explains every required environment variable.
- [x] README.md explains how to run the project.
- [x] README.md includes one example input.
- [x] README.md includes one short example output.
- [x] README.md describes each agent.
- [x] README.md describes each tool.
- [x] README.md includes a reflection.
- [x] README.md includes known limitations.
- [x] The project checks for an empty topic.
- [x] The project checks for missing configuration.
- [x] The project reports when Ollama is unavailable.
- [x] The project reports when the selected model is not installed.
- [x] The project reports validation failures clearly.
- [x] The project handles file-writing errors.
- [x] The real `.env` file is ignored by Git.
- [x] No real API key or secret is included in this README.

## Reflection

### What is the difference between a direct LLM call and an AI agent?

A direct LLM call sends a prompt to a model and returns its response. The application usually controls the prompt, receives the result and finishes that single interaction.

An AI agent adds a defined role, persistent instructions and a place within a larger workflow. An agent may receive context from earlier stages, use tools and produce output for another agent or deterministic process. In this project, the agents still use language-model calls internally, but their responsibilities and hand-offs are explicitly organised.

The agents are not autonomous in an unrestricted sense. `main.py` controls when each one runs and what information it receives.

### What role does each agent have in the system?

The Explainer Agent produces the educational explanation. It focuses on beginner-friendly language, key concepts, an example, common mistakes and a final summary.

The Practice Designer Agent converts the topic and explanation into a small practical exercise. It is separated from the Explainer Agent so that exercise design has a clear responsibility.

The Reviewer Agent performs quality control. It reviews the assembled draft and points out weaknesses without replacing the entire guide.

### What role does each tool have in the system?

The configuration loader checks whether the application has the information required to start.

The Ollama preflight tool checks an external dependency: the local model server and the configured model.

The validation tool enforces the required Markdown structure deterministically. It does not rely on the language model to decide whether headings are present.

The file-writing tool performs the final disk operation and reports file-system failures clearly.

The assembly functions in `main.py` combine agent outputs into one predictable document. They prevent the final structure from depending entirely on whether a small local model follows every formatting instruction.

### What was the most difficult part of the project?

The most difficult part was handling variable model output while still producing a reliable final document.

The local model sometimes changed heading levels, omitted sections or left a Markdown code fence open. An open code fence caused later headings to be interpreted as code, so validation reported several sections as missing even though the agents had run successfully.

The solution was to separate flexible generation from deterministic control. Agents generate the content, while Python assembles the final headings, repairs unmatched code fences, validates the structure and saves only valid output.

Configuration handling was another important difficulty. Agent logic could not run when `.env` values were missing, Ollama was stopped or the selected model had not been downloaded. Preflight checks made these failures easier to identify.

### What limitation was observed when using the selected model?

The selected `llama3.2:3b` model is small enough to run locally on modest hardware, but its instruction-following is inconsistent.

It may:

- change required Markdown headings;
- omit requested content;
- repeat part of the prompt;
- generate malformed or unclosed code blocks;
- provide vague reviewer comments;
- produce different results for the same topic on different runs.

Its explanations may also contain factual or pedagogical weaknesses. The deterministic validator can confirm structure, but it cannot prove that the content is correct.

A larger model could improve output quality, but it would require more memory, more processing time and potentially a stronger GPU or paid external API.

## Known Limitations

The project has the following limitations:

- Only the Ollama provider is currently supported by the configuration validator.
- Ollama must be running before the workflow starts.
- The configured model must already be downloaded locally.
- Local generation speed depends on hardware. CPU-only runs may be slow.
- The three agent calls run sequentially, so their generation times are added together.
- Model responses are non-deterministic and may differ between runs.
- The selected small model may ignore instructions or produce weak content.
- The validator checks headings and Markdown structure, not factual accuracy.
- Fallback text can make a document structurally valid even when an agent supplied poor content.
- The Reviewer Agent is itself model-based and may overlook errors or make unnecessary suggestions.
- Review comments are included in the guide, but the workflow does not automatically revise the criticised sections.
- The output file is replaced on every successful run rather than creating a separate file for each topic.
- The project does not currently provide automated unit tests or continuous integration.
- The project is intended as a learning exercise, not a production-ready educational system.
