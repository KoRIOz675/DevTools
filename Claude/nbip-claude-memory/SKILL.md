---
name: nbip-claude-memory
description: >
  Persist and update session memory into the project's CLAUDE.md file so that
  context survives across Claude Code CLI sessions. Use this skill whenever the
  user uses the commande "/nbip-claude-memory", or says things like "save memory", 
  "remember this", "memorize", "update CLAUDE.md", "save context", "save our progress", 
  or at the natural end of a working session. Also triggers automatically when the 
  conversation is wrapping up and meaningful decisions, architecture choices, or 
  task progress have been established. Always write memory content in English 
  regardless of the conversation language.
---

# Claude Memory Skill
 
Persist the current session's knowledge into `CLAUDE.md` at the project root so
future sessions pick it up automatically. Claude Code reads `CLAUDE.md` at
startup, making this the most efficient memory mechanism available.
 
--
 
## When this skill triggers
 
- **Explicit**: user enters "/nbip-claude-memory" or says "save memory", "remember this",
  "memorise that", "update CLAUDE.md", "sauvegarde", "mémorise", etc.
- **Implicit / end-of-session**: conversation is winding down and meaningful
  context has accumulated (decisions made, architecture discussed, tasks done).
---

## Step-by-step workflow
 
### 1. Extract memory from the conversation
 
Scan the full conversation and extract content for each of the four memory
sections below. Be concise but precise — prefer bullet points over prose.
**Always write extracted content in English.**
 
| Section | What to capture |
|---|---|
| `## Project Context` | Stack, language, frameworks, environment, repo structure highlights |
| `## Technical Decisions` | Architectural choices and the *reason* behind them |
| `## Tasks` | Completed work (✅) and remaining TODO (🔲), with enough detail to resume |
| `## Session Summary` | 3–8 bullet narrative of what happened this session |
 
Only populate sections where there is actual content. Skip empty sections.
 
---
 
### 2. Read the existing CLAUDE.md (if any)
 
```bash
cat CLAUDE.md 2>/dev/null || echo "__EMPTY__"
```
 
- If `__EMPTY__`: create from scratch using the template below.
- If it exists: perform a **merge** — replace each managed section with the
  updated version, preserve any content that is outside the managed sections
  (user-written instructions, project rules, etc.).
  
#### Identifying managed sections
 
Managed sections are delimited by sentinel comments:
 
```
<!-- claude-memory:start:<SECTION_NAME> -->
...content...
<!-- claude-memory:end:<SECTION_NAME> -->
```
 
Where `<SECTION_NAME>` is one of: `project-context`, `technical-decisions`,
`tasks`, `session-summary`.
 
If the existing file has no sentinels (first run), **append** the memory block
at the end after a clear separator.
 
---
 
### 3. Write CLAUDE.md
 
Use this template for the memory block. Always output valid Markdown.
 
```markdown
<!-- claude-memory:start:project-context -->
## Project Context
 
<!-- Fill with extracted stack/architecture info -->
<!-- claude-memory:end:project-context -->
 
<!-- claude-memory:start:technical-decisions -->
## Technical Decisions
 
<!-- Fill with decisions + rationale -->
<!-- claude-memory:end:technical-decisions -->
 
<!-- claude-memory:start:tasks -->
## Tasks
 
<!-- Fill with ✅ done and 🔲 todo items -->
<!-- claude-memory:end:tasks -->
 
<!-- claude-memory:start:session-summary -->
## Session Summary
_Last updated: <ISO date>_
 
<!-- Fill with 3–8 bullet narrative -->
<!-- claude-memory:end:session-summary -->
```
 
Write the file:
 
```bash
# Use a heredoc or write directly — always overwrite CLAUDE.md atomically
cat > CLAUDE.md << 'EOF'
<full merged content>
EOF
```
 
---
 
### 4. Confirm to the user
 
After writing, output a short confirmation in the user's language, e.g.:
 
> ✅ Memory saved to `CLAUDE.md` — 4 sections updated. Next session will resume
> from this context automatically.
 
List which sections were updated and how many items each contains.
 
---
 
## Merge algorithm (detail)
 
```
for each managed section in new memory:
    if sentinel block exists in current file:
        replace content between sentinels with new content
    else:
        append sentinel block at end of file
 
preserve all content outside sentinel blocks unchanged
```
 
Do **not** remove existing sentinel blocks even if the new session has nothing
to add to that section — keep the last known content instead.
 
---
 
## Quality rules
 
- **Concise**: each bullet ≤ 15 words. No filler sentences.
- **Actionable tasks**: every TODO must have enough context to act on without
  re-reading the conversation.
- **Decisions include rationale**: `Chose X over Y because Z` format.
- **No secrets**: never write API keys, passwords, tokens, or personal data.
- **English only**: all memory content must be in English, regardless of the
  conversation language.
- **Idempotent**: running the skill twice must produce the same result (no
  duplicate content).
---
 
## Example output
 
```markdown
<!-- claude-memory:start:project-context -->
## Project Context
 
- **Stack**: Next.js 14, TypeScript, Prisma, PostgreSQL
- **Auth**: NextAuth v5 with GitHub provider
- **Deploy target**: Vercel + Supabase
- **Monorepo**: `apps/web`, `packages/ui`, `packages/db`
<!-- claude-memory:end:project-context -->
 
<!-- claude-memory:start:technical-decisions -->
## Technical Decisions
 
- Chose Prisma over Drizzle: team familiarity, better Next.js integration
- Using RSC for data fetching; client components only for interactivity
- Opted for Supabase over PlanetScale: row-level security needed
<!-- claude-memory:end:technical-decisions -->
 
<!-- claude-memory:start:tasks -->
## Tasks
 
- ✅ Set up monorepo structure with Turborepo
- ✅ Configure NextAuth with GitHub OAuth
- ✅ Define Prisma schema (User, Post, Comment)
- 🔲 Implement post creation UI (`apps/web/app/posts/new`)
- 🔲 Add pagination to feed (cursor-based, see `PostFeed` component)
- 🔲 Write migration for soft-delete on Post model
<!-- claude-memory:end:tasks -->
 
<!-- claude-memory:start:session-summary -->
## Session Summary
_Last updated: 2025-11-14_
 
- Bootstrapped the monorepo and installed core dependencies
- Resolved TypeScript path alias issue in `packages/ui`
- Designed and applied initial Prisma schema
- Discussed pagination strategy; chose cursor-based over offset
- Auth flow tested locally, GitHub OAuth working end-to-end
<!-- claude-memory:end:session-summary -->
```
 
