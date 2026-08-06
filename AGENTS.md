# Repository AI Agent Guidelines

This repository (`mlai-lab`) is a modular environment for machine learning, deep learning, time-series forecasting, and AI experiments.

## Core Development Rules

1. **Notebook-First Workflow**:
   - Prefer Jupyter notebook-first workflows for exploratory data analysis, feature prototyping, model experimentation, and decision signal evaluation.
   - Keep notebooks reproducible, readable, and executable top-to-bottom using local project paths.

2. **Avoid Unnecessary App Infrastructure**:
   - Do not scaffold full web applications, FastAPI services, Docker microservices, or complex backend infrastructure for personal notebook analysis tasks unless explicitly requested by the user.

3. **Strict SKU & VRAM Separation**:
   - In hardware/GPU price tracking tasks (e.g. NVIDIA RTX 50 series), NEVER mix product SKUs across VRAM variants (e.g., RTX 5060 Ti 8GB vs 16GB must always be separate SKUs and separate features).

4. **Modular Utility Design**:
   - Prefer small, clean Python helper modules (`src/*.py`) for data IO, cleaning, feature building, and model evaluation over monolithic scripts or heavy frameworks.

5. **Realistic Sample Data & Provenance**:
   - When creating offline/sample datasets, use plausible domain numbers (e.g., realistic INR GPU pricing) and document data provenance and assumptions in workspace documentation.
