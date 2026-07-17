# QAlchemy

**A configuration-driven AI framework for building reusable AI-powered capabilities.**

QAlchemy is a modular Python framework for developing intelligent, maintainable, and reusable AI-powered applications. Rather than creating one-off AI scripts, QAlchemy provides a clean, extensible architecture that separates AI infrastructure from business logic, allowing developers to build scalable AI capabilities that evolve over time.

Built around a service-oriented, configuration-driven architecture, QAlchemy provides reusable components for prompt management, AI provider integration, runtime execution, reporting, and workflow orchestration while remaining independent of any specific application domain.

---

# Features

## AI Framework

- Configuration-driven architecture
- Modular service-oriented design
- AI provider abstraction
- Configurable model selection
- Prompt management and composition
- Runtime execution context
- Markdown report generation
- Template-based output
- Extensible capability architecture

## AI Integration

- Multi-provider AI client architecture
- Local and cloud model support
- Standardized AI request pipeline
- Prompt engineering framework
- Configurable runtime behavior
- Reusable workflow components

## Software Architecture

- Strong separation of concerns
- Dependency-driven design
- Strongly typed configuration
- Reusable infrastructure services
- Extensible framework components
- Framework-first development
- Testable architecture

---

# Why QAlchemy?

Most AI projects begin as small scripts that quickly become difficult to maintain, extend, and reuse.

QAlchemy was created to provide a reusable foundation for building AI-powered applications by separating common AI infrastructure from domain-specific capabilities.

Instead of rewriting the same AI plumbing for every project, developers can focus on building capabilities while QAlchemy handles:

- AI provider integration
- Prompt management
- Runtime configuration
- Reporting
- Workflow execution
- Configuration management

The result is a clean, maintainable architecture that scales from simple prompt execution to sophisticated AI automation.

---

# Quick Start

```bash
git clone https://github.com/<your-github-account>/qalchemy.git

cd qalchemy

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Configure your preferred AI provider in:

```
framework.yaml
```

Run one of the included capabilities:

```bash
python scripts/generate_code.py
```

or

```bash
python scripts/review_code.py
```

---

# Architecture

```
                 User / CLI
                      │
                      ▼
             AI Capability Service
                      │
           ┌──────────┴──────────┐
           │                     │
    Prompt Builder        Runtime Context
           │                     │
           ▼                     ▼
    Prompt Loader          Report Writer
           │                     │
           └──────────┬──────────┘
                      ▼
              AI Client Builder
                      │
                      ▼
                  AI Client
                      │
          Local / Cloud Provider
                      │
                      ▼
               AI Generated Result
```

---

# Current Capabilities

- AI-assisted code generation
- AI-assisted code review
- Prompt management
- AI provider abstraction
- Runtime execution context
- Configuration-driven execution
- Markdown report generation
- Template-based output
- External validation framework

---

# Technology Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.13 |
| AI Providers | Ollama (Extensible) |
| Configuration | YAML |
| Testing | pytest |
| Reporting | Markdown |
| Architecture | Service-Oriented |
| Version Control | Git / GitHub |

---

# Project Structure

```
qalchemy/
│
├── clients/
├── services/
├── prompts/
├── templates/
├── scripts/
├── tests/
├── docs/
├── framework.yaml
├── reporting.py
└── runtime_context.py
```

---

# Roadmap

## Version 1.0

- Configuration-driven framework
- Prompt Builder
- Prompt Loader
- AI Client abstraction
- Runtime Context
- Report Writer
- Code Generation capability
- Code Review capability
- External validation
- Comprehensive unit testing
- GitHub Actions CI

## Future Enhancements

- Additional AI providers
- Document review
- Image analysis
- Requirements analysis
- Test generation
- Capability plug-in architecture
- Workflow orchestration
- RAG integration
- Vector database support
- Multi-language code generation

---

# Contributing

Contributions, feature requests, and suggestions are welcome.

As QAlchemy evolves, the goal is to provide a flexible framework for building reusable AI-powered capabilities across multiple domains.

---

# License

This project is licensed under the MIT License.