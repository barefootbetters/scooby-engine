# ewiki theme

Proprietary. Copyright Barefoot Betters. All rights reserved. Use requires written permission.

The shared Hugo theme for the Barefoot Betters ewikis. One core, reconciled
from the four hand-rolled copies the wikis grew apart (D-24727), plus a closed
set of extension points. Each wiki supplies its config, its brand tokens and
logo, and those extension partials, and nothing else.

What every wiki gets from the core:

- a sidebar and content grid, with a Pagefind search box in the header
- an "On this page" table of contents on longer pages
- heading anchors, a skip link and breadcrumbs
- dark mode, from the reader's `prefers-color-scheme`
- one link resolver that turns GitHub-style relative links into wiki pages
- an "Editing this page" footer built from params
- the `include-section`, `audio`, `audio-inline` and `swatch` shortcodes

The core emits no JavaScript except the Pagefind loader,
`<script data-wiki-search>`, and only when search is on (D-24293). It never
reads the clock, so two builds of a wiki are byte-identical.

## Install

The theme is vendored, not fetched: a wiki commits a tagged copy under
`<site>/themes/ewiki/`, so its CI never needs network access or credentials
for this private repo (D-24728).

1. Clone this repo next to the wiki, and check out the release tag.
2. Vendor it:

   ```pwsh
   pwsh -File ../ewiki-theme/tools/Sync-EwikiTheme.ps1 -Version v1.0.0 -Target themes/ewiki
   ```

   Sync extracts `layouts assets tools theme.toml README.md` at that tag with
   `git archive` (autocrlf off), replaces `themes/ewiki/`, and writes
   `THEME-VERSION` and `.theme-manifest.txt`. It prints the manifest digest.
   Check that it equals the digest in the tag's GitHub release notes.

3. In the wiki's `hugo.toml`, set `theme = "ewiki"`. A wiki that runs Hugo
   from its repo root also sets `themesDir` (corporate memory:
   `themesDir = "viewer/themes"`).
4. Copy the site-config keys below into the wiki's own `hugo.toml`. The theme
   ships no config of its own and doesn't rely on Hugo's theme-config merging.
5. Pin the digest in the wiki's CI and run the checks (below).

## Site config the wiki owns

These keys keep the build deterministic and the theme's features working.
Each wiki keeps them in its own `hugo.toml`:

```toml
enableGitInfo = false
disableHugoGeneratorInject = true
disableKinds = ["RSS", "sitemap"]   # add "taxonomy", "term" for a one-page tags index

[markup]
  [markup.highlight]
    codeFences = false              # Chroma's inline output isn't stable between builds
  [markup.goldmark.renderer]
    unsafe = false
  [markup.goldmark.parser]
    autoHeadingID = true
    autoHeadingIDType = "github"
  [markup.tableOfContents]
    startLevel = 2
    endLevel = 4
```

A wiki whose content root holds images mounts them at
`assets/<contentRoot>`, so the render hooks can find each one by its
content-relative path. Herbs' `docs/` mount is the model:

```toml
[[module.mounts]]
  source = "../../docs"
  target = "assets/docs"
  files = ["**/*.{png,jpg,jpeg,gif,svg,webp,avif}"]
```

## Params

Set under `[params.ewiki]`. Defaults are applied in the templates.

| Param | Type | Default | Meaning |
|---|---|---|---|
| `repo` | string | (required) | GitHub `owner/name` for blob, tree and edit links |
| `branch` | string | `"main"` | Branch for those links |
| `contentRoot` | string | `""` | Repo path that maps to the Hugo content root (engine `wiki`, herbs `docs`, corporate memory `""`). Used for GitHub URLs and the footer only. |
| `localRoot` | string | `""` | Local checkout path shown in "Editing this page"; omitted when empty |
| `homeSource` | string | `""` | Content-relative file whose links go to `/` (engine `INDEX.md`, corporate memory `README.md`) |
| `private` | bool | `true` | Emit `noindex, nofollow` |
| `search` | bool | `true` | Render the Pagefind stub and loader |
| `searchPlaceholder` | string | `"Search the wiki"` | Stub placeholder |
| `searchLabel` | string | `"Search the wiki"` | Stub aria-label |
| `titlePrefix` | string | `""` | Prefix stripped from titles in lists, the sidebar and breadcrumbs |
| `logo` | string | `""` | Asset path of the header logo; omitted when empty |
| `toc` | bool | `true` | Render the table of contents |
| `tocMinHeadings` | int | `3` | Minimum h2-h4 count before the TOC renders |
| `breadcrumbs` | bool | `true` | Render breadcrumbs (never on the home page) |
| `headingAnchors` | bool | `true` | Render heading anchor links |
| `editingFooter` | bool | `true` | Render "Editing this page" |
| `sectionReadme` | bool | `false` | Since v1.1.0. A section whose `_index.md` has no body text (or that has none) shows its folders `README.md` as its landing text, and leaves that README out of its page list |
| `folderLinks` | string | `"github"` | Since v1.1.0. `"section"` sends a link ending in `/` that names a rendered section to that section page; any other folder link still goes to GitHub |

Page params the core reads:

- `links_from: repo-root`: the page's links are written from the repository
  root (a generated inventory), so none is looked up as a page.
- `canonical-source` (and optional `canonical-source-repo`): the page mirrors
  a document that owns its text; the footer sends the editor there.
- `sortByWeight`, `sortByFile`: on a section's `_index.md`, sort its page list
  by `weight` or by file name instead of by title.

## How links resolve

Links are written for GitHub: relative to the linking file. The link hook
resolves each one from the page's own folder, content-relative. The branches
are numbered as in `render-link.html`; the first match wins:

- **1.** A URL with a scheme (`https:`, `mailto:`), an anchor (`#...`) or a
  root-relative path (`/...`) passes through.
- **2.** A link whose text is a single image, pointing at an image file,
  opens the file full size in a new tab.
- **3.** A path ending in `/` goes to the folder on GitHub (`tree`). With
  `folderLinks = "section"`, a folder that is a rendered section goes to that
  section page instead.
- **4.** An image file under the content root goes to its published copy, as
  a download.
- **4a.** On a `links_from: repo-root` page, every other link goes to GitHub
  at the path as written.
- **5.** The `homeSource` file goes to the home page.
- **6.** A path that names a page goes to that page (with its `#fragment`).
- **7.** Anything else goes to GitHub (`blob`). A link to a `.md` or an image
  inside the content root that names nothing warns, so a `--panicOnWarning`
  build fails on it.

A path that climbs out of the content root (`../...`) is never looked up as a
page; it goes to GitHub.

## Extension points

A wiki overrides these by placing a same-named file in its own `layouts/` or
`assets/`. Each partial receives the page being rendered.

| File | What it holds | Default |
|---|---|---|
| `partials/ewiki/sidebar.html` | the sidebar navigation body | sections and their pages, by title |
| `partials/ewiki/metadata.html` | the metadata panel's fields | updated/created and tags |
| `partials/ewiki/after-content.html` | anything after the body (related pages, sources) | nothing |
| `partials/ewiki/editing-extra.html` | the wiki's own "Editing this page" paragraphs | nothing |
| `partials/ewiki/head-end.html` | extra tags at the end of `<head>` | nothing |
| `partials/ewiki/body-end.html` | extra markup at the end of `<body>` | nothing |
| `assets/css/ewiki-brand.css` | every custom property, light and dark | engine light, herbs dark |
| `assets/css/ewiki-site.css` | the wiki's own selectors | empty |

A wiki may also add its own shortcodes, render hooks the theme doesn't ship
(herbs' `render-codeblock-mermaid.html`), a home layout (`home.html` or
`index.html`), and section layouts under `layouts/<section>/`.

Every other theme file under `layouts/`, plus `assets/css/ewiki.css`, is
**core**. A wiki may not shadow a core file, by any of Hugo's equivalent
layout paths or through a module mount. `Test-EwikiTheme.ps1` fails if it
does. A change to a core file goes to this repo, then a re-sync.

A script element added through `head-end` or `body-end` is the wiki's own to
gate; the theme's one-script guarantee covers core output only.

## The CSS order

The stylesheet is one bundle, `css/ewiki.bundle.css`, joined in this order:

1. `ewiki-brand.css`: every custom property, in a light `:root` block and then
   a dark `@media (prefers-color-scheme: dark)` block.
2. `ewiki.css`: the core rules. They read tokens through `var()` only and
   declare none.
3. `ewiki-site.css`: the wiki's own selectors. It may not declare a custom
   property either.

Only the brand file defines tokens, and its dark block comes last within it,
so nothing can override dark mode by accident. A wiki's brand file must define
every token the default brand file defines, light and dark. Changing this
order is a major release.

## The vendored copy is read-only

Three checks keep a vendored copy from drifting:

- **The manifest.** `.theme-manifest.txt` lists every vendored file's
  SHA-256, hashed over LF-normalized text, so Windows and Linux checkouts
  agree.
- **The pinned digest.** The wiki's CI pins the manifest's own SHA-256
  outside `themes/ewiki/`, in its workflow. An edit plus a regenerated
  manifest still fails.
- **The shadow check.** `Test-EwikiTheme.ps1` fails on any consumer file that
  shadows a core file.

Before it runs the vendored checker, the wiki's CI verifies the manifest and
the checker from outside, with plain shell, so an edited checker can't certify
itself:

```bash
pinned="<digest from the release notes>"
manifest_digest=$(tr -d '\r' < themes/ewiki/.theme-manifest.txt | sha256sum | cut -d' ' -f1)
[ "$manifest_digest" = "$pinned" ] || { echo "The vendored theme manifest doesn't match the pinned digest." >&2; exit 1; }
checker_hash=$(tr -d '\r' < themes/ewiki/tools/Test-EwikiTheme.ps1 | sha256sum | cut -d' ' -f1)
grep -qx "$checker_hash  tools/Test-EwikiTheme.ps1" themes/ewiki/.theme-manifest.txt || { echo "The vendored Test-EwikiTheme.ps1 doesn't match its manifest line." >&2; exit 1; }
pwsh -File themes/ewiki/tools/Test-EwikiTheme.ps1 -Site . -ExpectedManifestSha256 "$pinned"
```

## The tools

All four are vendored under `themes/ewiki/tools/` and run with `pwsh` 7.

- **`Sync-EwikiTheme.ps1 -Version <tag|HEAD> -Target <site>/themes/ewiki`**
  vendors a version (run it from a theme clone).
- **`Test-EwikiTheme.ps1 -Site <dir> [-Config <file>] [-ExpectedManifestSha256 <hex>]`**
  checks the vendored copy against its manifest and the pinned digest, and
  checks the site for core shadows. It is self-contained, so the shell check
  above covers it.
- **`Invoke-WikiGates.ps1 -Site <dir> [-Config <file>] [-ContentDir <dir>] [-ExpectedPageCount <n>] [-PanicOnWarning]`**
  runs the engine ewiki's five build gates: the build, page-count equality,
  two-build determinism, the Pagefind index (`pagefind` 1.5.2) and the
  JS-free scan.
- **`Compare-WikiBuild.ps1 -Baseline <public> -Candidate <public>`** compares
  two builds of a wiki: the page set, every link and image in `<main>`, and
  the visible text. A migration packet runs it against the wiki's own
  pre-migration build.

`-Site` is the Hugo project directory (`hugo --source`). `-Config` defaults to
`<Site>/hugo.toml`; mounts resolve against `-Site`, as Hugo resolves them. The
gates' output folder is the config's `publishDir`, defaulting to
`<Site>/public`.

A wiki whose content arrives through mounts passes `-ExpectedPageCount`, and
its workflow computes that number at run time from the mounted source files.
A hard-coded number is a static floor that goes stale; the glob belongs to
each wiki, because only the wiki knows its mounts.

## Upgrading

1. Read the release notes of the new tag. A major release changes a param
   name, a core file path, the extension-point list or the CSS order, and its
   notes say what a wiki has to change.
2. Re-run Sync with the new tag.
3. Replace the pinned digest with the one in the new tag's release notes.
4. Run the wiki's gates, and `Compare-WikiBuild.ps1` against the previous
   build, before merging.

Releases are annotated tags, `vMAJOR.MINOR.PATCH`. A new opt-in feature is a
minor release; a fix is a patch.
