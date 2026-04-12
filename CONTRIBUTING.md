# Contributing to RoboForge AI

Thanks for your interest! This project is built incrementally in 22 phases
(see `~/.claude/plans/kind-gathering-llama.md`). Each phase = one focused
session = one git commit.

## Ground rules (token-budget discipline)

These rules exist so that any contributor — human or AI — can work on a
single module without loading the rest of the repo.

1. **Per-file cap ~200 lines.** Split if growing.
2. **Scoped `CLAUDE.md` per module.** Each module dir owns a `CLAUDE.md`
   declaring its purpose, public surface, allowed imports, and forbidden
   cross-module reads.
3. **No cross-module imports except via interfaces.** `agents/` may import
   `providers/base` but not `providers/claude`. Enforced by `import-linter`.
4. **Skeleton-first.** Files are stamped with stub interfaces in early
   phases; later phases fill them — no architectural drift.
5. **Generators for repetition.** Use `scripts/make-provider.ts` and
   `scripts/make-agent.ts` to scaffold new providers/agents from templates.
6. **One phase = one commit.** Use the conventional commit messages from
   the build plan (e.g., `feat(providers): base + claude`).

## Workflow

1. Pick the next unbuilt phase from the plan.
2. Read only the files listed in that phase's "Read" column.
3. Write the files listed in the phase's "Write" column.
4. Run the phase's verification command.
5. Commit using the phase's commit template.

## Code style

- **Frontend:** TypeScript strict, ESLint, Prettier; Tailwind for styling.
- **Backend:** Python 3.11, ruff (lint+format), mypy strict, pytest.
- **Schemas:** JSON Schema drafts in `shared/schemas/` are the single source
  of truth. Never hand-edit `shared/ts/` or `shared/py/` — run `pnpm codegen`.

## License

By contributing you agree your contributions are licensed under MIT.
