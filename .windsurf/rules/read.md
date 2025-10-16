---
trigger: manual
description: 
globs: 
---

MANDATORY FILE READING PROTOCOL:

READ FILES FROM DISK/STORAGE FIRST
- Do not rely on memory or cached information
- Fetch the actual file content from storage every single time
- Do not pretend to know file contents without reading them
- If a file is mentioned or referenced, read it immediately from disk

COMPLETE CONTEXT UNDERSTANDING
- Read through the entire file/codebase without skipping parts
- Understand how all components interact
- Identify root causes, not surface symptoms
- Don't be lazy or make assumptions
- Don't read from memory, always read from storage

NO SHORTCUTS
- Read from storage, not memory
- Don't drop important details to save time
- Don't skip files or sections
- Don't make assumptions about file content
- Every file reference must be fetched fresh from disk

If anything's ambiguous, ask clarifying questions.