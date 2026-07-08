# MedRef Design System

## 1. Core Principles
- **Clinical & Professional**: MedRef is a medical reference tool, not a playful conversational chatbot. The UI must inspire trust, competence, and precision.
- **High Data Density**: Medical professionals need to scan information rapidly. Minimize excessive whitespace; optimize for readability and structured scanning.
- **Structured Outputs**: Information should be presented in distinct, logical sections (e.g., Warnings, Dosing, Interactions) rather than uniform chat bubbles.
- **Accessibility (a11y) First**: Adhere to WCAG 2.1 AA standards. Ensure high contrast, screen reader compatibility, and full keyboard navigation.

## 2. Visual Language

### Color Palette
A calm, sterile palette reduces cognitive load and eye strain during long clinical shifts.
- **Primary Brand**: Slate Blue (`#0f172a`) - Used for headers, primary actions.
- **Background**: Soft Gray/Off-White (`#f8fafc`) - Prevents the stark harshness of pure white.
- **Surface**: Pure White (`#ffffff`) - For distinct answer cards.
- **Accents**: 
  - **Clinical Teal** (`#0d9488`): Used for interactive elements (citations, links).
  - **Warning Red** (`#ef4444`): Used strictly for contraindications and severe clinical warnings.

### Typography
- **Font Family**: Inter (sans-serif) for optimal legibility at small sizes.
- **Hierarchy**:
  - `h1`: 24px, Semi-Bold (Page Titles)
  - `h2`: 18px, Medium (Section Headers)
  - `body`: 14px, Regular (Standard Text)
  - `small`: 12px, Regular (Citations, Metadata)

## 3. Component Standards (shadcn/ui)

### Answer Cards
- Responses are **not** rendered as chat bubbles. They are rendered as full-width **Answer Cards** resembling a textbook or reference portal.
- **Structure**:
  - **Query Header**: Re-states the clinical query clearly.
  - **Content Body**: The retrieved, generated answer.
  - **Citations Footer**: A distinct section listing all sources used.

### Citations (HoverCard)
- Citations must be inline `[1]`, formatted with the Clinical Teal accent.
- Must utilize a `HoverCard` component: On hover, it displays a small popup containing the exact source snippet and the document name, allowing rapid fact-checking without leaving the context.

### Medical Disclaimer Alert
- Every Answer Card must conclude with a muted `Alert` component stating: *"Clinical judgment remains with the treating physician."*

## 4. Accessibility (a11y) Guidelines
- **Color Contrast**: All text must maintain a minimum 4.5:1 contrast ratio against its background.
- **Focus States**: All interactive elements (citations, buttons, search bars) must have a clearly visible focus ring (e.g., `ring-2 ring-slate-400 focus:outline-none`).
- **ARIA Labels**: All icon buttons and complex interactive components must utilize descriptive `aria-label` tags.
