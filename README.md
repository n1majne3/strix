<p align="center">
  <a href="https://strix.ai/">
    <img src="https://github.com/usestrix/.github/raw/main/imgs/cover.png" alt="Strix Banner" width="100%">
  </a>
</p>

<div align="center">

# Strix (Fork)

### Enhanced fork with native SDK providers, prompt caching, extended thinking, and lazy skill loading.

Fork of [usestrix/strix](https://github.com/usestrix/strix) — open-source AI hackers to find and fix your app's vulnerabilities.

<br/>

[<img src="https://github.com/usestrix/.github/raw/main/imgs/Discord.png" height="40" alt="Join Discord">](https://discord.gg/strix-ai)
[<img src="https://github.com/usestrix/.github/raw/main/imgs/X.png" height="40" alt="Follow on X">](https://x.com/strix_ai)

</div>

---

## What's Changed from Upstream

This fork enhances the LLM layer with several improvements over the upstream [usestrix/strix](https://github.com/usestrix/strix):

### Native SDK Providers

The LLM layer has been rewritten from a LiteLLM-only backend to a **dual native SDK provider architecture**:

- **AnthropicProvider** — Uses the native `anthropic` Python SDK with full Anthropic Messages API support
- **OpenAIProvider** — Uses the native `openai` Python SDK with streaming and usage tracking

A `ProviderBase` abstract class provides a unified interface, and `get_provider()` auto-selects based on the canonical model name.

### Anthropic-Specific Enhancements

- **Prompt caching** — Automatic `cache_control` markers on system prompts and last user message for Anthropic prompt caching (reduces cost and latency)
- **Extended thinking** — Configurable thinking budgets mapped from reasoning effort levels (`low`/`medium`/`high`)
- **Streaming tool calls** — Partial tool-call state streamed in real-time, not just at completion
- **Message format conversion** — Automatic OpenAI-to-Anthropic message translation (tool calls, tool results, consecutive user message merging)

### Lazy Skill Loading

Skills are categorized into **essential** (always loaded into the system prompt) and **deferred** (loaded on-demand). This reduces token usage on startup while keeping capabilities available when needed.

### Real Cost Tracking

Both providers calculate actual costs per request using litellm's pricing database, with static fallback pricing tables for newer models.

---

## Strix Overview

Strix are autonomous AI agents that act just like real hackers — they run your code dynamically, find vulnerabilities, and validate them through actual proof-of-concepts. Built for developers and security teams who need fast, accurate security testing without the overhead of manual pentesting or the false positives of static analysis tools.

**Key Capabilities:**

- **Full hacker toolkit** out of the box
- **Teams of agents** that collaborate and scale
- **Real validation** with PoCs, not false positives
- **Developer-first** CLI with actionable reports
- **Auto-fix & reporting** to accelerate remediation


## Use Cases

- **Application Security Testing** - Detect and validate critical vulnerabilities in your applications
- **Rapid Penetration Testing** - Get penetration tests done in hours, not weeks, with compliance reports
- **Bug Bounty Automation** - Automate bug bounty research and generate PoCs for faster reporting
- **CI/CD Integration** - Run tests in CI/CD to block vulnerabilities before reaching production

## Quick Start

**Prerequisites:**
- Docker (running)
- An LLM API key from any supported provider (OpenAI, Anthropic, Google, etc.)

### Installation & First Scan

```bash
# Install Strix
curl -sSL https://strix.ai/install | bash

# Configure your AI provider
export STRIX_LLM="openai/gpt-5.4"
export LLM_API_KEY="your-api-key"

# Run your first security assessment
strix --target ./app-directory
```

> [!NOTE]
> First run automatically pulls the sandbox Docker image. Results are saved to `strix_runs/<run-name>`

---

## Architecture

### Provider System

The LLM layer uses a provider-based architecture:

```
LLMConfig  -->  get_provider()  -->  AnthropicProvider (anthropic/ models)
                                -->  OpenAIProvider    (openai/ models)
```

Each provider implements the `ProviderBase` interface with:
- `generate_stream()` — Streaming LLM responses with partial tool-call state
- `supports_vision()` / `supports_reasoning()` / `supports_prompt_caching()` — Capability detection
- `should_retry()` — Retryable error detection (429, 500, 502, 503)
- `get_stats()` — Accumulated token usage and cost

### Anthropic Provider

Uses the native `anthropic` AsyncAnthropic client with:

| Feature | Details |
|---------|---------|
| Prompt caching | `cache_control: ephemeral` on system and last user message |
| Extended thinking | Budget mapped from effort: `low` (4K), `medium` (16K), `high` (64K) |
| Tool calling | Full OpenAI-to-Anthropic message format conversion |
| Streaming | Real-time tool-call state + thinking blocks |

### OpenAI Provider

Uses the native `openai` AsyncOpenAI client with:

| Feature | Details |
|---------|---------|
| Streaming | `stream_options: include_usage` for token tracking |
| Tool calling | Native function calling with streaming deltas |
| Cost tracking | Cached token detection from `prompt_tokens_details` |

### Skill Loading

Skills are loaded in two phases:

1. **Startup-loaded**: `root-agent` via `essential: true`, the selected scan mode (`quick`, `standard`, or `deep`), and white-box-only skills when `is_whitebox=True`
2. **Deferred** (on-demand): non-startup skills such as `sql-injection`, `xss`, `nmap`, and `fastapi`

Deferred skills are loaded via the `load_skill` tool when the agent needs them.

---

## Features

### Agentic Security Tools

Strix agents come equipped with a comprehensive security testing toolkit:

- **Full HTTP Proxy** - Full request/response manipulation and analysis
- **Browser Automation** - Multi-tab browser for testing of XSS, CSRF, auth flows
- **Terminal Environments** - Interactive shells for command execution and testing
- **Python Runtime** - Custom exploit development and validation
- **Reconnaissance** - Automated OSINT and attack surface mapping
- **Code Analysis** - Static and dynamic analysis capabilities
- **Knowledge Management** - Structured findings and attack documentation

### Comprehensive Vulnerability Detection

Strix can identify and validate a wide range of security vulnerabilities:

- **Access Control** - IDOR, privilege escalation, auth bypass
- **Injection Attacks** - SQL, NoSQL, command injection
- **Server-Side** - SSRF, XXE, deserialization flaws
- **Client-Side** - XSS, prototype pollution, DOM vulnerabilities
- **Business Logic** - Race conditions, workflow manipulation
- **Authentication** - JWT vulnerabilities, session management
- **Infrastructure** - Misconfigurations, exposed services

### Graph of Agents

Advanced multi-agent orchestration for comprehensive security testing:

- **Distributed Workflows** - Specialized agents for different attacks and assets
- **Scalable Testing** - Parallel execution for fast comprehensive coverage
- **Dynamic Coordination** - Agents collaborate and share discoveries

---

## Usage Examples

### Basic Usage

```bash
# Scan a local codebase
strix --target ./app-directory

# Security review of a GitHub repository
strix --target https://github.com/org/repo

# Black-box web application assessment
strix --target https://your-app.com
```

### Advanced Testing Scenarios

```bash
# Grey-box authenticated testing
strix --target https://your-app.com --instruction "Perform authenticated testing using credentials: user:pass"

# Multi-target testing (source code + deployed app)
strix -t https://github.com/org/app -t https://your-app.com

# White-box source-aware scan (local repository)
strix --target ./app-directory --scan-mode standard

# Focused testing with custom instructions
strix --target api.your-app.com --instruction "Focus on business logic flaws and IDOR vulnerabilities"

# Provide detailed instructions through file (e.g., rules of engagement, scope, exclusions)
strix --target api.your-app.com --instruction-file ./instruction.md

# Force PR diff-scope against a specific base branch
strix -n --target ./ --scan-mode quick --scope-mode diff --diff-base origin/main
```

### Headless Mode

Run Strix programmatically without interactive UI using the `-n/--non-interactive` flag — perfect for servers and automated jobs. The CLI prints real-time vulnerability findings and the final report before exiting. Exits with non-zero code when vulnerabilities are found.

```bash
strix -n --target https://your-app.com
```

### CI/CD (GitHub Actions)

Strix can be added to your pipeline to run a security test on pull requests with a lightweight GitHub Actions workflow:

```yaml
name: strix-penetration-test

on:
  pull_request:

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: Install Strix
        run: curl -sSL https://strix.ai/install | bash

      - name: Run Strix
        env:
          STRIX_LLM: ${{ secrets.STRIX_LLM }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}

        run: strix -n -t ./ --scan-mode quick
```

### Configuration

```bash
export STRIX_LLM="openai/gpt-5.4"
export LLM_API_KEY="your-api-key"

# Optional
export LLM_API_BASE="your-api-base-url"  # if using a local model, e.g. Ollama, LMStudio
export PERPLEXITY_API_KEY="your-api-key"  # for search capabilities
export STRIX_REASONING_EFFORT="high"  # control thinking effort (default: high, quick scan: medium)
```

> [!NOTE]
> Strix automatically saves your configuration to `~/.strix/cli-config.json`, so you don't have to re-enter it on every run.

**Supported providers:**

| Provider | Model ID | Notes |
|----------|----------|-------|
| OpenAI | `openai/gpt-5.4` | Native SDK, streaming + usage tracking |
| Anthropic | `anthropic/claude-sonnet-4-6` | Native SDK, prompt caching + extended thinking |
| Anthropic | `anthropic/claude-opus-4-6` | Native SDK, prompt caching + extended thinking |
| Others | LiteLLM format | Routed through LiteLLM compatibility layer |

---

## Development

### Prerequisites

- Python 3.12+
- Docker (running)
- [uv](https://docs.astral.sh/uv/) for dependency management

### Setup

```bash
git clone https://github.com/n1majne3/strix.git
cd strix
uv sync
uv run pre-commit install
```

### Running Tests

```bash
# All tests with coverage
make test

# Specific test suites
uv run pytest tests/llm/                    # LLM provider tests
uv run pytest tests/llm/test_provider_anthropic.py  # Anthropic-specific
uv run pytest tests/llm/test_provider_openai.py     # OpenAI-specific

# Lint and type check
make check-all
```

---

## Documentation

Full documentation is available at [docs.strix.ai](https://docs.strix.ai).

Local preview:

```bash
npm i -g mintlify
cd docs && mintlify dev
```

---

## Contributing

We welcome contributions — see the [Contributing Guide](CONTRIBUTING.md) to get started.

## Acknowledgements

Fork of [usestrix/strix](https://github.com/usestrix/strix). Strix builds on the incredible work of open-source projects like [LiteLLM](https://github.com/BerriAI/litellm), [Caido](https://github.com/caido/caido), [Nuclei](https://github.com/projectdiscovery/nuclei), [Playwright](https://github.com/microsoft/playwright), and [Textual](https://github.com/Textualize/textual). Huge thanks to their maintainers!


> [!WARNING]
> Only test apps you own or have permission to test. You are responsible for using Strix ethically and legally.

</div>
