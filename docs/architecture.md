## Component: `ai/reporting.py` (`ReportWriter`)

## Architecture Overview

```mermaid
flowchart TD
  CLI[CLI Script\nreview_source_code.py] --> CRS[CodeReviewService]
  CRS --> PBS[PromptBuilderService]
  PBS --> PLS[PromptLoaderService]
  CRS --> AIBS[AIClientBuilderService]
  AIBS --> AIC[AIClient]
  AIC --> OLLAMA[Ollama]
  CRS --> RC[RuntimeContext]
  CLI --> RW[ReportWriter]
  RW --> ACS[AppConfigurationService]
  RW --> FS[(File System)]
  RC --> RW
```

## Report Generation Sequence

```mermaid
sequenceDiagram
  participant CLI as review_source_code.py
  participant CRS as CodeReviewService
  participant PBS as PromptBuilderService
  participant AIBS as AIClientBuilderService
  participant AIC as AIClient
  participant RW as ReportWriter
  participant FS as File System

  CLI->>CRS: execute(source_code, runtime_context)
  CRS->>PBS: build_prompt(review_instructions, user_prompt)
  PBS-->>CRS: system_prompt, user_prompt
  CRS->>AIBS: build(model_override)
  AIBS-->>CRS: AIClient
  CRS->>AIC: generate(system_prompt, user_prompt)
  AIC-->>CRS: review markdown
  CRS-->>CLI: review markdown + updated runtime_context

  CLI->>RW: write(review, runtime_context)
  RW->>FS: create destination directory
  RW->>FS: write markdown report
  RW-->>CLI: destination path
```

### Purpose
Formats and persists Markdown review reports to disk.

### Responsibilities
- Load report template from framework configuration.
- Build review metadata table (source file, model, execution time).
- Render final Markdown report content.
- Ensure destination directory exists.
- Write report file and return output path.

### Upstream Dependencies (Who calls this)
- Main review orchestration/service layer (caller passes `review`, `source_file`, `destination`, `model`, `execution_time`).
- Any workflow that needs persisted AI review output.

### Downstream Dependencies (What this component uses)
- `services.app_configuration_service.AppConfigurationService`
  - Reads:
    - `reports.review.template`
    - `reports.review.fields.*`
- `pathlib.Path`
  - Reads template file.
  - Creates destination directories.
  - Writes report files.

### Data Flow
`Review Content + Metadata -> ReportWriter -> Markdown Render -> File System -> Report Path`

### Current Notes
- `lines_reviewed` and `review_date` are implemented in `_build_review_information` and controlled by `reports.review.fields`.

## Configuration Mapping

```mermaid
flowchart LR
  FW[app.yaml] --> P1[prompts.root]
  FW --> P2[prompts.code_standards]
  FW --> P3[prompts.python_standards]
  FW --> P4[prompts.playwright_standards]
  FW --> P5[prompts.generation_instructions]
  FW --> P6[prompts.review_instructions]
  FW --> T1[templates.root]
  FW --> T2[templates.code_review_report]
  FW --> R1[reports.output_root]
  FW --> R2[reports.review.fields.*]

  P1 --> PLS[PromptLoaderService]
  P2 --> PBS[PromptBuilderService]
  P3 --> PBS
  P4 --> PBS
  P5 --> CGS[CodeGenerationService]
  P6 --> CRS[CodeReviewService]
  T1 --> RW[ReportWriter]
  T2 --> RW
  R1 --> RW
  R2 --> RW
```