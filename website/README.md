# Process guide website

The GitHub Pages guide explains the provisioning-to-publication process. It is
an explanatory view of the Markdown specifications, not a separate contract
authority. Wire schemas and the contract-set version are unchanged.

## Build and preview

Python 3.12 or newer; no additional dependencies:

```sh
python tools/build_site.py
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000`. The build reads `VERSION` and `docs/catalog.md`,
generates the coverage counts and catalog table, pins specification links to the
checked-out commit, and checks local files, anchors and repository source paths.
All assets are relative, so the site works under the `/kaiba-contracts/` Pages
project path. Navigation uses native links; no JavaScript or remote assets are
required.

Edit `website/index.html` for the narrative and `website/styles.css` for styling.
Update the dated implementation snapshot when project status changes; preserve
the distinction between specified schemas, experimental implementations and
production adoption. Changes to the authoritative catalog automatically appear
in the next build. Add detail links in `tools/build_site.py` when specifying a
new contract.

## GitHub Pages setup

The `Process guide · GitHub Pages` workflow builds and checks the site on pull
requests. Pushes to `main` and manual runs on `main` also deploy the artifact.
Pull requests never deploy. The separate contract validation workflow continues
to check schemas and fixtures.

For the initial repository setup, open
[Settings → Pages](https://github.com/pd-codex/kaiba-contracts/settings/pages),
then choose **GitHub Actions** under **Build and deployment → Source**. No extra
workflow template or token secret is needed. If a deployment ran before Pages
was enabled, rerun its failed jobs or use **Run workflow** on the
[Pages workflow](https://github.com/pd-codex/kaiba-contracts/actions/workflows/pages.yml).

After a successful deployment, the expected default project URL is
<https://pd-codex.github.io/kaiba-contracts/>. The deployment job exposes the
actual published URL through the `github-pages` environment.

Initial enablement requires repository administration; the workflow's normal
`GITHUB_TOKEN` cannot enable a disabled Pages site. See GitHub's
[publishing-source documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
and the official
[`configure-pages` inputs](https://github.com/actions/configure-pages/blob/v5/action.yml).
