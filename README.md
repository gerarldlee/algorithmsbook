# Algorithmic Foundations, Distributed Systems & AI Architecture

A Hugo + Hextra book covering algorithms, system design, distributed systems, cloud
engineering, and production machine-learning infrastructure.

## Project structure

- `content/` — book chapters, navigation pages, and reference material.
- `TOC.md` — canonical 15-chapter outline and scope.
- `TASKS.md` — implementation checklist derived from the outline and authoring rules.
- `archetypes/default.md` — chapter template used by Hugo.
- `layouts/` — project-specific rendering hooks.
- `tools/check_links.py` — link, front-matter, weight, naming, and heading checks.
- `hugo.yaml` — site configuration.

Generated Hugo output belongs in `public/` and `resources/`; `.hugo_build.lock` is also
generated. These files are ignored and should not be edited or committed.

## Requirements

- Hugo Extended `0.159.2`
- Go, for the Hextra module
- Python, for repository checks

Hextra is imported as a Go module. Do not add a `themes/` directory or a theme submodule.

## Local development

Start a live preview with `hugo server`. Include drafts and future-dated pages with
`hugo server -D -F`.

Before publishing a change, run a production build with `hugo --gc --minify`, then run
`python tools/check_links.py`. The build and checker are the acceptance tests for content
changes.

## Writing chapters

Read `AGENTS.md` before editing Markdown. In summary:

- Use YAML front matter and keep filename prefixes, weights, and navigation entries aligned.
- Follow the standard chapter sections and keep `Related` last.
- Algorithm chapters provide equivalent Java, C, Python, Rust, TypeScript, and Go examples
	in that order. The header language selector filters those algorithm examples and remembers
	the selected language.
- Tag every code fence and keep prose and diagrams theme-neutral.
- Use relative links for internal content and update `TOC.md` and `TASKS.md` when scope changes.

## Task tracking

Use `TASKS.md` for chapter and infrastructure work. Mark a checkbox only when the corresponding
implementation has been completed and validated. Keep `TOC.md` as the outline source of truth;
`TASKS.md` is the working checklist.
