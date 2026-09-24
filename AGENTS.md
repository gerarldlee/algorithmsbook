# AGENTS.md — instructions for writing Markdown in this book

Hugo + [Hextra](https://imfing.github.io/hextra/) static site. Everything a reader sees is
Markdown under `content/`. Read this file before creating or editing any `.md` file there.
Keep it in sync when a convention changes: it is the authoring spec, and `tools/check_links.py`
enforces the parts that can be checked mechanically.

## 1. Repo in one screen

| Piece | What it is |
| --- | --- |
| `hugo.yaml` | Site config: menus, author/footer params, `editURL`, markup (raw HTML allowed, math passthrough delimiters). |
| `go.mod` / `go.sum` | Hextra `v0.12.3` imported as a **Go module**. There is deliberately no `themes/` directory and no git submodule — do not re-add one. |
| `content/` | All prose. `content/docs/**` = the book; `content/_index.md` = home; `content/about.md` = about page. |
| `TOC.md` | Canonical expanded outline; the implemented book currently reaches Chapter 15, while later topics remain future scope. Keep implemented pages and navigation synchronized as sections are added (and vice versa). |
| `archetypes/default.md` | Template used by `hugo new`: derives `title`/`weight` from the filename and emits the §5 skeleton. |
| `layouts/_markup/render-link.html` | Project-level link render hook. Hextra's own hook only rewrites destinations that begin with `/`; this one also resolves **relative** destinations, which is what the content uses (§9). |
| `tools/check_links.py` | Relative-link/front-matter/weight checker (`python tools/check_links.py`). |
| `.github/workflows/pages.yaml` | CI: build with Hugo `0.159.2` and deploy to GitHub Pages on push to `main`. |
| `public/`, `resources/`, `.hugo_build.lock` | Generated output, gitignored. **Never edit or commit.** |

Current content shape: 132 Markdown files — 93 chapters (Part I 28, II 14, III 11, IV 12, V 13,
VI 15), 8 `00-essentials` reference pages, 27 `_index.md` navigation pages, `content/about.md`,
`content/guide.md`, `content/table-of-contents.md`, `content/terms-of-use.md`, and `content/_index.md`. All 93 chapters open with the §5 sections in that order.

## 2. Book requirements → what they mean when you write

These are the product and authoring requirements for the book. Keep the implementation rules below
consistent with the language, theme, and content requirements they describe.

| Requirement | Concrete rule in Markdown |
| --- | --- |
| Every algorithm written in Java, Go, Python, C, Rust and TypeScript | Each algorithm chapter carries **one fenced block per language, in the fixed order `java`, `c`, `python`, `rust`, `typescript`, `go`**, as a single contiguous group (§6). |
| The reader chooses their preferred language | Fence tags must be exactly those six ids — a language switcher keys off them — and the group must be machine-collapsible: identical tab order/names in every group on a page (§6). |
| Choosing a language shows **all** examples in that language | One language per fence, never mixed; language-specific prose lives inside that language's own block as a comment; keep every group on a page in the same order so a synced selector can drive them all (§6). |
| System, dark and light themes | Never hard-code colours, `style="…"`, `<font>` or background classes; write plain Markdown/tables/shortcodes so both themes render (§10). Diagrams via ```` ```mermaid ```` inherit the theme automatically (§6). |

## 3. Commands

| Task | Command |
| --- | --- |
| Live preview | `hugo server` → <http://localhost:1313> |
| Preview drafts/future pages | `hugo server -D -F` |
| Scaffold a chapter (fills front matter + skeleton) | `hugo new content docs/<NN-part>/<NN-category>/<NN-slug>.md` |
| Production build (identical to CI output) | `hugo --gc --minify` |
| Link/weight/naming checks | `python tools/check_links.py` |
| Refresh the theme module after editing `go.mod` or `module.imports` | `hugo mod tidy` |

- Build with **Hugo extended 0.159.2** (pinned in `.github/workflows/pages.yaml` and
  `.devcontainer/devcontainer.json`). Hextra v0.12.3 uses the new `layouts/_shortcodes`,
  `_partials`, `_markup` layout conventions — older Hugo releases will not render it.
- A clean production build and a clean link check are the acceptance test for content changes;
  there is no other test suite. The build **fails loudly** (`errorf` from the render hook) when an
  internal `.md`/directory link cannot be resolved, so a typo cannot ship silently.
- KaTeX and Mermaid assets are fetched from jsDelivr at build time, so pages using them need network
  access; a failed fetch aborts the build. (`site.Params.mermaid.base`/`js` can point at local
  copies.)
- `draft: true` pages are excluded from `hugo --gc --minify` (hence from the deployed site).
- The build does **not** prune `public/`: HTML for a deleted or renamed page lingers there (and would
  be deployed). Delete `public/` or pass `--cleanDestinationDir` when you rename or remove pages.
- Line endings are mixed and that is intentional: chapters are LF, `_index.md` and the
  `00-essentials` pages are CRLF. Never mass-normalize them — it produces whole-file diffs.

## 4. Front matter contract

Every content file starts with **YAML** front matter delimited by `---`. All 132 files use YAML;
never use TOML `+++`.

```yaml
---
title: "Hash Tables and Hash Sets"
weight: 4
toc: true
---
```

| Key | Rule |
| --- | --- |
| `title` | Quoted string, Title Case, same as the `_index.md` link text. No trailing period. |
| `weight` | Integer. For numbered chapter files, it must equal the two-digit filename prefix. For category indexes, it follows the canonical TOC order and must be unique among siblings. |
| `toc` | `toc: true` on chapters (explicit, even though Hextra defaults to `true`). Omit on `_index.md`, `content/about.md` and the `00-essentials` reference pages. `toc: false` hides the right-hand in-page TOC. |
| `next` / `prev` | Only used to override the Hextra pager link; `content/docs/_index.md` sets `next: 01-algorithms`. |
| `type` | Only `content/about.md` (`type: about`). Section/category `_index.md` files get a plain docs page. |
| `tabs` | Not used. The header language selector filters tagged fences directly; keep the six language fences in the fixed order (§6). |
| `draft` | Never in committed content. `hugo new` emits `draft: true`, so remove the key once the chapter is written; drafts are previewed with `hugo server -D` and are excluded from the production build. |

## 5. Chapter skeleton

Path: `content/docs/<NN-part>/<NN-category>/<NN-slug>.md`
(e.g. `content/docs/01-algorithms/01-linear-data-structures/04-hash-tables.md`).
Slug is kebab-case, no spaces, prefix `NN` = `weight`.

Use `##` for chapter sections and avoid `# H1` headings because the page title comes from front
matter (`tools/check_links.py` fails the check when one appears). Use `###` subheadings sparingly
when they improve clarity.
Keep to these sections, in this order, with these exact names:

| Section | Required | Content |
| --- | --- | --- |
| `## What it is` | yes | One paragraph: definition, the problem it solves, the mental model. First sentence stands alone as the definition. |
| `## How it works` | yes | The mechanism, in execution order, prose first and code after. Name the real systems/languages that implement it. |
| `## Complexity` | optional, mutually exclusive with `Tradeoffs` | Only when per-operation costs are the point. Markdown table, first column = operation/algorithm. |
| `## Tradeoffs` | optional, mutually exclusive with `Complexity` | Only when there is a genuine design tradeoff. `- **Option** — gain, then cost.` bullets or a `\| Property \| Gain \| Cost \|` table. |
| `## When to use` | yes | 3–6 bullets, each phrased as a condition the reader can check ("You need X …"). |
| `## Alternatives` | yes | Bullets: `**Named alternative** — when it wins, and what it costs.` |
| `## Related` | yes | Relative links to neighbouring pages. Always the **last** section. |

All 93 chapters have the five required sections in this order, `Related` last. `Complexity` (39
chapters) and `Tradeoffs` (54) are mutually exclusive in today's content and sit immediately after
`How it works`; pick the one that fits the topic. Extra `##` sections are not used in the current
outline, and `###` sub-headings are used sparingly (15 in the whole book) — prefer folding material
into the canonical sections.

Complexity tables in use (any of these shapes is fine — pick the one that fits, keep the header):

```markdown
| Operation | Time | Space |
| --- | --- | --- |
| Access by index | O(1) | O(1) |
| Append at end | O(1) amortized | O(1) |
```

Use `O(1)`, `O(n log n)`, `O(n)` amortized; say *amortized* explicitly when it applies, and
annotate code with the same notation in a trailing comment (`// amortized O(1)`).

## 6. Code blocks and the six-language contract

**Always tag the fence** (`java`, `c`, `python`, `rust`, `typescript`, `go`, `yaml`, `bash`, `sql`,
`proto`, `mermaid`, `json`, `http`, `graphql`, `hcl`, `text`, `dockerfile`, `prometheus`) — there are zero untagged fences in the book today; an untagged block is
invisible to the language switcher and gets no syntax highlighting.

**Algorithm chapters are polyglot.** The six blocks form one contiguous group, in this order:

| # | Fence | Type names | Method names |
| --- | --- | --- | --- |
| 1 | `java` | `HashTable`, `UnionFind` | `camelCase` (`addNode`) |
| 2 | `c` | `Entry`, `DynamicArray` | `snake_case` with a type prefix (`ht_put`, `uf_find`, `da_push`) |
| 3 | `python` | `HashTable` | `snake_case` (`add_node`), `__init__` for the constructor |
| 4 | `rust` | `HashTable` | `snake_case` (`add_node`) |
| 5 | `typescript` | `HashTable` | `camelCase` (`addNode`) |
| 6 | `go` | `HashTable` | exported `PascalCase` (`AddNode`) |

- **Type names stay identical across languages** (verified: `HashTable`, `UnionFind`,
  `ConsistentHash`, `Entry`); only the calling convention changes. The reader switching tabs must see
  the same API in a different dialect, not a different program.
- Every language implements the **same operation set and the same algorithm** — no language gets a
  simplified version.
- **Compliance today: complete.** All 28 Part I chapters carry one contiguous six-language group, and
  so do the five algorithm-bearing chapters elsewhere (the three caching chapters, `06-sharding`,
  `01-vector-databases`). `01-dynamic-arrays.md` adds four extra complete six-language groups to
  illustrate array declaration, indexed access, iteration, and linear search — extra groups are fine,
  an *incomplete group* is not.
- Prose that is language-specific belongs inside that language's fenced block as a comment, so the
  header selector can hide it with the block.
- The header language selector is available on every page. Preserve the same language order and names
  across all groups. The selector filters the tagged code fences directly; do not wrap algorithm groups
  in synchronized-tab shortcodes.

**Systems chapters (Parts II–VI)** lead with the artifact that shows the mechanism — Kubernetes YAML,
Terraform/HCL, Cloudflare config, GitHub Actions, protocol/state-machine descriptions — and add
implementation code only when the chapter teaches an algorithm (then use the six-language group).
`yaml` is the most common fence in those parts (58 uses book-wide).

**Diagrams** use ```` ```mermaid ````; Hextra renders it, loads Mermaid from the CDN, and switches
the diagram theme with the reader's light/dark choice, so never bake colours into diagram nodes.

**`00-essentials`** is reference material, not algorithm chapters. It uses the fixed six-language
groups where it teaches implementation detail; do not add ad hoc language mixes there.

## 7. Math

Math passthrough is configured in `hugo.yaml`, so use those delimiters — nothing else:

- inline: `\( O(n \log n) \)`
- display: `\[ ... \]` or `$$ ... $$`

Hextra detects math per page and loads KaTeX automatically (`site.Params.math.engine`, default
`katex`) — no `math: true` front matter needed. KaTeX is fetched from jsDelivr at build time, so a
math-bearing page needs network access to build cleanly. Only 20 pages currently use math; prefer
plain text or a code block unless the notation genuinely helps.

## 8. Shortcodes

Hextra v0.12.3 shortcodes available: `cards`/`card` (used on the home page), `callout`, `details`,
`tabs`/`tab`, `steps`, `filetree`, `badge`, `icon`, `include`, `jupyter`, `pdf`, `term`, `asciinema`.

```markdown
{{< callout type="info" >}}
Body text. Types: default, info, warning, error, important. Markdown (bold, links, lists) renders
inside the body — the shortcode markdownifies its inner content itself.
{{< /callout >}}
```

Introduce shortcodes sparingly: cards are used on the home page, and the header language selector is
implemented with a site asset. Keep algorithm language groups synchronized by fence order and tags
as described in §6; do not wrap them in tab shortcodes.

## 9. Links and navigation integrity

- Internal links are **relative to the current file**: sibling `02-linked-lists.md`, section
  `../02-search-trees/01-binary-search-trees.md`, cross-part `../../00-essentials/06-memory-works-templates.md`,
  category directory `01-linear-data-structures/`. Never write site-absolute URLs (`/docs/...`) or
  GitHub blob URLs for content in this repo.
- Relative links are resolved to page permalinks at build time by `layouts/_markup/render-link.html`
  (Hugo does not publish `.md` files, and Hextra's built-in hook only rewrites `/`-prefixed
  destinations — without this hook every internal link would 404 on the deployed site). Keeping the
  sources relative also means the links still work when the Markdown is browsed on GitHub, so
  **never delete that hook** and re-sync it if Hextra's own `render-link.html` changes.
- The destination must resolve to a page or page resource (`GetPage`/`Resources.Get`), not merely to
  a file on disk: linking a chapter's directory works because it is a section, linking to a
  non-section file by an extensionless path may not. Unresolvable `.md` and directory links abort
  the build.
- Links inside shortcode bodies (`tabs`, `callout`) resolve too: Hugo renders inner shortcode
  Markdown with the *home* page as context, so the hook falls back to a context-free suffix match.
  That match must be unique, so inside a shortcode prefer the qualified form
  (`../02-search-trees/01-binary-search-trees.md`) over a bare basename.
- Every new page **must** be added to its parent `_index.md` bullet list, in `weight` order, with the
  same text as its `title` and a `NN-slug.md` (or `NN-category/`) target.
- New categories/parts must also be added to `content/docs/_index.md` (Part lists) and, for a new
  part, to the table of contents in `content/_index.md`.
- External sources go into the References page (`content/docs/00-essentials/08-references.md`), not
  inline as bare URLs.
- Images: the book has none yet. If you add one, put the file in `assets/` (processed by Hugo) or
  `static/`, and reference it site-absolute (`/images/foo.png`); Hextra's image hook resolves that
  form for both, and page-bundle resources work as well.
- Run `python tools/check_links.py` after any link or file move; it also reports missing front
  matter, `weight`/filename mismatches, duplicate weights, unlisted pages, and stray `# H1`s.
  (Current state: 132 files checked, 0 problems.)

## 10. Prose style

- Third person, present tense, active voice; address the reader as "you".
- Section opens with the conclusion, then the mechanism. No preamble, no "in this section we will…".
- Define a term the first time you use it; bold key terms (`**quorum**`) on first use.
- Concrete over abstract: name ZooKeeper/etcd/Raft/Cloudflare/DynamoDB instead of "some system".
- American English. No emojis. No `TODO` markers — finish the section or leave it out.
- Tables for comparisons, bullets for decision rules and enumerations, prose for mechanisms.
- **Theme-neutral formatting**: no `style=`, no `<font>`, no hard-coded colours or background
  classes (the book has zero today). Tables, bold, callouts and Mermaid diagrams are already
  theme-aware for system/light/dark.
- Every claim about behaviour or cost should be checkable; state the source of numbers or drop them.

## 11. Checklist: adding a chapter

1. Pick the folder and number: `content/docs/<NN-part>/<NN-category>/<NN-slug>.md`. To insert in the
   middle, renumber the files after it **and** update each `weight`, the parent `_index.md` list, and
   any `Related` links pointing at moved files.
2. `hugo new content docs/<part>/<category>/<NN-slug>.md` → fills the §4 front matter (YAML `---`,
   quoted `title`, `weight` = prefix, `toc: true`, `draft: true`) and the §5 skeleton.
3. Write the §5 sections in order; add `Complexity` or `Tradeoffs`, never both.
4. For an algorithm topic, write the full six-language group of §6 — same algorithm, same type
   names, same operation set, in the fixed order — instead of a single-language snippet.
5. Add the page to the parent `_index.md` bullet list at the right position — until you do, the page
   is unreachable from the sidebar and `tools/check_links.py` reports it.
6. Add `Related` links to the 2–4 nearest pages, and add reciprocal links from those pages' `Related`.
7. Mirror the new section in `TOC.md`.
8. Remove `draft: true`.
9. `hugo --gc --minify` → must build with no warnings; then `python tools/check_links.py`.
10. Open the rendered page (`hugo server`, or `public/docs/.../index.html`) and check the sidebar
    position, TOC entries, that all six languages are present and in order, and that nothing
    overflows in code blocks — including in dark mode.

## 12. Checklist: adding a category or part

1. Create `content/docs/<NN-part>/<NN-category>/_index.md` with `title` and `weight` = the folder's
   number, plus the intro sentence and the bullet list of children (same wording as their `title`s).
2. Link the new category from the part's `_index.md`, or the new part from `content/docs/_index.md`
   and from the home page TOC in `content/_index.md`.
3. Keep `weight` ordering consistent with the on-disk numbering; Hextra sorts by `weight`, so a
   missing `weight` silently reorders the sidebar.
4. Rebuild and re-run the link checker.

## 13. Do not

- Do not edit `public/`, `resources/`, or `.hugo_build.lock`.
- Do not add a `themes/` directory or a git submodule for Hextra; bump `go.mod` + `hugo mod tidy`.
- Do not delete or bypass `layouts/_markup/render-link.html`, and do not expect
  `markup.goldmark.renderHooks.link.enableDefault` to help: Hextra ships its own `render-link.html`,
  which takes precedence, and only understands `/`-prefixed destinations.
- Do not ship an algorithm chapter that is missing a language from the §6 group, mixes two languages
  in one fence, uses `js`/`ts`/`cpp` instead of `typescript`/`c`, or leaves a fence untagged.
- Do not hard-code colours or inline styles (breaks the system/dark/light requirement).
- Do not use TOML front matter, `# H1` headings, or absolute internal links.
- Do not renumber files without updating `weight`, the parent `_index.md`, and inbound `Related` links.
