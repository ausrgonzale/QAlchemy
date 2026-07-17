QAlchemy Demonstration
======================

Purpose
-------
This demonstration showcases the core capabilities of the QAlchemy
framework by generating Python source code and performing an AI
code review.

Prerequisites
-------------
- Python environment activated
- QAlchemy dependencies installed
- framework.yaml configured
- AI provider available (Ollama, OpenAI, Anthropic, etc.)

Run
---
From the project root:

    python -m demo.demo_framework

Output
------
Generated source code:

    demo/sample_code/calculator.py

Generated review report:

    demo/output/calculator_review.md

Notes
-----
This demonstration also serves as the framework's end-to-end
acceptance test and exercises the complete workflow:

    Configuration
        ↓
    Prompt Loading
        ↓
    AI Code Generation
        ↓
    Source File Creation
        ↓
    AI Code Review
        ↓
    Markdown Report Generation