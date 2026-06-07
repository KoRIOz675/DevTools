---
name: pdf-to-notes
description: >
  Convert a PDF file into one or more clean, structured Obsidian markdown notes.
  Use this skill whenever the user provides a PDF and asks to convert it, import it,
  take notes from it, or add it to their vault — even if they phrase it casually
  ("turn this PDF into notes", "import this lecture", "make this readable in Obsidian").
  Handles course slides, research papers, technical documentation, and multi-chapter books.
  Always produces nested output under 03 - Knowledge/course-name/ with an index.md.
---

# PDF to Obsidian Notes

Converts a PDF into clean, structured Obsidian markdown notes with YAML frontmatter,
wikilinks to existing vault notes, callouts, and a course index.

**Invocation**: `pdf-to-notes <file.pdf> [course-name]` — `course-name` is optional;
if omitted, infer it from the PDF filename and content.

---

## Step 0 — Read the vault settings

```bash
cat "99 - Claude Code/config/vault-settings.md"
```

Store:
- `KNOWLEDGE_FOLDER` — default `03 - Knowledge`
- `LANGUE` — default `EN`

---

## Step 1 — Discover existing vault notes

Build a reference list so wikilinks only point to notes that actually exist.

```bash
# All markdown files in the vault (excluding 99 - Claude Code/)
find . -name "*.md" \
  -not -path "./99 - Claude Code/*" \
  -not -name "index.md" \
  | sed 's|^\./||' | sed 's|\.md$||'
```

Also read any `index.md` files found in the knowledge folder, since they often list
sub-notes that may not be discoverable by filename alone:

```bash
find "[KNOWLEDGE_FOLDER]" -name "index.md" | while read f; do echo "=== $f ==="; cat "$f"; done
```

Store the combined result as `EXISTING_NOTES` — a flat list of note stems
(e.g. `03 - Knowledge/Algorithms/01-complexity`).

---

## Step 2 — Extract and parse the PDF

```bash
pip install markitdown[pdf] --break-system-packages -q
python3 - <<'EOF'
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("PATH_TO_PDF")
print(result.text_content)
EOF
```

markitdown outputs markdown directly — headings, tables, and lists are already
partially structured, which reduces the work needed in Step 4.

If extraction yields garbled text or fewer than 200 words → warn the user:
*"The PDF appears to be scanned or image-based. OCR is needed for better results — consider running `ocrmypdf` on it first. I'll do my best with what's extractable."*

Store the markdown output as `RAW_TEXT`.

---

## Step 3 — Infer course name and structure

From `RAW_TEXT` and the PDF filename, determine:

- `COURSE_NAME` — human-readable name (e.g. `Advanced Algorithms`, `DevSecOps Fundamentals`)
- `COURSE_SLUG` — filesystem-safe slug (e.g. `advanced-algorithms`)
- `OUTPUT_DIR` — `[KNOWLEDGE_FOLDER]/[COURSE_NAME]/`
- `SECTION_COUNT` — estimated number of logical sections/chapters

**Splitting heuristic** — create one note per logical section:
- Slides deck: one note per major topic block (not per slide)
- Research paper: one note per section (Abstract, Introduction, Method, Results, Discussion, Conclusion)
- Technical doc: one note per chapter or H1
- Short document (<2000 words): single note

If structure is ambiguous → default to splitting at H1-level headings.

---

## Step 4 — Clean and transform content

Apply these transformations to each section before writing:

### 4.1 — Strip noise
Remove:
- Slide/page number markers: `Slide N`, `Page N / M`, `- N -`, standalone integers on their own line
- Author bio lines: lines containing `@`, `linkedin.com`, `PhD`, `Professor at`, `University of`
- Copyright/watermark text: `©`, `All rights reserved`, `Confidential`, `Draft`
- Repeated headers that are identical across sections (boilerplate course title repeats)
- Excessive blank lines (max 2 consecutive)

### 4.2 — Fix heading hierarchy
markitdown already maps some headings — review and correct rather than rebuild from scratch:
- The note title (frontmatter `title`) is H1 — do not repeat it as `# Heading` in the body
- First-level sections → `##`
- Sub-sections → `###`
- Never skip levels (no H4 unless H3 exists above it)
- Orphaned single-word headers with no body → merge into the paragraph below or remove

### 4.3 — Fix bullet fragments
Bullets that are incomplete sentence fragments (no verb, < 6 words) →
- If 3 or fewer fragments in a row: convert to a short prose sentence
- If 4+ fragments: keep as bullets but complete each to a full sentence

### 4.4 — Fix tables
markitdown converts well-structured PDF tables to GFM automatically. For any remaining
ASCII tables (using `+`, `-`, `|`) → convert to proper GFM markdown tables:
```
+--------+--------+     →     | Col A | Col B |
| val    | val    |           |-------|-------|
+--------+--------+           | val   | val   |
```
If a table has no header row → infer column names from context or use generic `Col 1`, `Col 2`.

### 4.5 — Add callouts
Use these rules consistently:

| Callout | When to use |
|---------|------------|
| `> [!NOTE]` | Side information, caveats, "note that…", warnings, edge cases |
| `> [!KEY]` | Definitions, core concepts, takeaways marked as important in the source |
| `> [!EXAMPLE]` | Concrete examples, case studies, worked problems, "for instance…" |

Format:
```markdown
> [!KEY] Term
> Definition or core statement here.
```

Do not over-callout — aim for 1–3 callouts per note, on the most significant content only.

### 4.6 — Add overview paragraph
At the top of the body (after frontmatter), add a 2–4 sentence overview paragraph
summarising what this note covers and why it matters. Write it in `LANGUE`.

---

## Step 5 — Add wikilinks

After cleaning, scan each note for concepts, terms, and topics that match
entries in `EXISTING_NOTES` (Step 1).

Matching rules:
- Case-insensitive match on the note stem (filename without extension)
- Only link the **first occurrence** of a term per note
- Format: `[[stem|display text]]` if the stem differs from the natural phrasing,
  otherwise `[[stem]]`
- Never auto-link generic words (`algorithm`, `function`, `data`) — only proper
  named concepts that map to a specific existing note
- Add matching stems to the frontmatter `related` list as well

---

## Step 6 — Build frontmatter

For each note, generate:

```yaml
---
title: "Human-readable note title"
course: "COURSE_NAME"
tags:
  - inferred-tag-1
  - inferred-tag-2
related:
  - "[[linked-note-stem]]"
created: YYYY-MM-DD   # today's date
source: "Original PDF filename"
---
```

Tag inference rules:
- Always include the course slug as a tag
- Add 2–5 topical tags inferred from content (kebab-case, lowercase)
- Never add generic tags like `note`, `lecture`, `document`

---

## Step 7 — Write notes to disk

```bash
mkdir -p "[OUTPUT_DIR]"
```

File naming convention: `NN-slug.md` where `NN` is a zero-padded sequence number
matching the order of sections (e.g. `01-introduction.md`, `02-complexity.md`).

Write each note. Do not overwrite existing files — if a file exists, append `_new`
to the name and warn the user.

---

## Step 8 — Generate index.md

Create `[OUTPUT_DIR]/index.md` adapting its structure to the content type:

**Always include:**
- YAML frontmatter with `title`, `course`, `tags`, `created`
- A 2–4 sentence description of the course/document
- A navigation table listing all generated notes

**Navigation table** (always):
```markdown
| # | Note | Summary |
|---|------|---------|
| 1 | [[01-introduction]] | What the course covers and why it matters |
| 2 | [[02-complexity]] | Big-O notation, time and space complexity |
```

**Add these sections only when content warrants it:**

- **Key concepts** — glossary-style list of the 5–10 most important terms with one-line definitions; use `> [!KEY]` for the top 3
- **Cross-cutting themes** — table of recurring themes and which notes cover them (only if 4+ notes exist)
- **Prerequisites** — wikilinks to notes the reader should know first (only if dependencies are explicit in the source)
- **Further reading** — external references cited in the PDF (only if present)

---

## Step 9 — Summary

Print a summary:

```
✅ Course: [COURSE_NAME]
✅ Output: [OUTPUT_DIR]
✅ Notes created: N files
   - 01-introduction.md
   - 02-...
✅ Index: [OUTPUT_DIR]/index.md
⚠️  [any warnings: scanned PDF, skipped files, etc.]
```

---

## Absolute rules

- **Never overwrite** existing notes without warning — use `_new` suffix
- **Only create wikilinks to notes confirmed in `EXISTING_NOTES`** — no speculative links
- **One H1 maximum per file** — the title in frontmatter counts as H1; do not add `# heading` at top of body
- **Write in `LANGUE`** — match the vault language setting, except for proper nouns from the source
- **Callouts sparingly** — 1–3 per note maximum; never callout entire sections
