# QAlchemy

**A configuration-driven AI engineering framework for building reusable AI-powered capabilities.**

QAlchemy is a modular Python framework for developing maintainable, reusable, and extensible AI-powered applications. Rather than building one-off AI scripts, QAlchemy provides a service-oriented architecture that separates AI infrastructure from business capabilities, allowing developers to build intelligent software that evolves over time.

---

# Version 1.1 Highlights

QAlchemy v1.1 focuses on strengthening the framework's infrastructure and execution pipeline while maintaining a clean, reusable architecture.

## New Infrastructure

- Centralized **AppConfigurationService** for strongly typed application configuration.
- New **Logging Service** providing a consistent framework logging API.
- New **Exception Handling Service** with a centralized exception catalog and typed framework exceptions.
- Enhanced **Prompt Builder** based on AI Work Orders.
- Expanded automated test suite with **110 passing unit tests**.

## Execution Pipeline

Version 1.1 establishes the foundation for a consistent AI execution pipeline.

```text
Application
     │
     ▼
Configuration
     │
     ▼
AI Work Order
     │
     ▼
Prompt Builder
     │
     ▼
AI Client
     │
     ▼
Generated Result
     │
     ▼
Reporting
```

The Logging Service and Exception Handling Service are now part of the framework infrastructure and positioned for future integration throughout the execution pipeline.

---

# Current Capabilities

- AI-assisted Code Generation
- AI-assisted Code Review
- Configuration-driven execution
- Prompt management and composition
- AI provider abstraction
- Runtime execution context
- Markdown report generation
- Template-based reporting
- Strongly typed configuration
- Service-oriented architecture

---

# Why QAlchemy?

Most AI projects begin as small scripts that quickly become difficult to maintain, extend, and reuse.

QAlchemy provides a reusable engineering foundation by separating common AI infrastructure from application-specific capabilities.

Developers focus on solving business problems while QAlchemy provides:

- AI provider integration
- Prompt construction
- Configuration management
- Runtime execution
- Reporting
- Logging infrastructure
- Exception handling infrastructure

---

# Quick Start

Clone the repository.

```bash
git clone https://github.com/ausrgonzale/QAlchemy.git

cd QAlchemy

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Configure your AI provider in:

```
config/app.yaml
```

Generate source code:

```bash
python -m scripts.feature.generate_code \
    --instructions "Create a production-ready TemperatureConverter class." \
    --output src_ai/temperature_converter.py
```

Review source code:

```bash
python -m scripts.feature.review_source_code \
    src_ai/temperature_converter.py
```

---

# Architecture

```text
          Application
               │
               ▼
       Feature Entry Point
               │
               ▼
      Feature Service
               │
      ┌────────┴─────────┐
      ▼                  ▼
Prompt Builder     Runtime Context
      │                  │
      ▼                  ▼
Prompt Loader      Report Writer
      │
      ▼
AI Client Builder
      │
      ▼
AI Provider
      │
      ▼
Generated Result
```

---

# Technology Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.13 |
| AI Providers | Ollama |
| Configuration | YAML |
| Testing | pytest |
| Reporting | Markdown |
| Architecture | Service-Oriented |
| Version Control | Git / GitHub |

---

# Project Structure

```text
qalchemy/
│
├── clients/
├── config/
├── prompts/
├── reports/
├── scripts/
│   ├── core/
│   └── feature/
├── services/
│   ├── core/
│   └── feature/
├── templates/
├── tests/
├── docs/
└── README.md
```

---

# Project History

## Version 1.0

Version 1.0 established the core AI engineering framework, including:

- AI Client abstraction
- Prompt Builder
- Prompt Loader
- Runtime Context
- Report Writer
- Code Generation capability
- Code Review capability
- Configuration-driven architecture
- Comprehensive automated testing

## Version 1.1

Version 1.1 focused on strengthening the framework's infrastructure and preparing QAlchemy for future capabilities.

Major additions include:

- AppConfigurationService
- Logging Service
- Exception Handling Service
- AI Work Order–driven prompt construction
- Enhanced execution pipeline
- 110 automated unit tests

The Logging and Exception Handling services are intentionally delivered as independent framework components in this release. Future releases will integrate these services throughout the execution pipeline while preserving the framework's separation of concerns.

---

# Roadmap

Future releases will continue expanding the framework with additional AI engineering capabilities, including:

- Interface adapters
- Enhanced execution pipeline
- Additional AI providers
- Requirements evaluation
- Document analysis
- Test generation
- Capability plug-in architecture
- Workflow orchestration

---

# Contributing

Contributions, suggestions, and feature requests are welcome.

QAlchemy is designed as a reusable AI engineering framework that continues to evolve through practical application and iterative improvement.

---

# License

This project is licensed under the MIT License.