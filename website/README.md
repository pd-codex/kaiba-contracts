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
project path. The process guide uses native navigation without JavaScript.
The interactive workflow uses local JavaScript modules; neither page needs remote
assets or calls to an API.

## Interactive workflow

`walkthrough.html` follows the device through nine steps: **entry state → operations
→ exit state**. Changed state dimensions are highlighted after each simulated
operation. Physical preparation, identity, fleet eligibility, configuration intent,
desired assignment and observed runtime remain distinct. The contract inspector
and acceptance rules are expandable supporting detail. Choose a reviewed hypothetical publication, the current development
block, a desired-state revision conflict, or a lost acceptance response. A gate
must pass before the next step unlocks. An identical retry in the lost-response
scenario recovers the existing publication without creating a second acceptance.
Restarting or changing scenarios clears all in-memory state.

The pure teaching state model lives in `website/walkthrough-model.mjs`, presentation
in `website/walkthrough.mjs`, and page styling in `website/walkthrough.css`.
`website/device-transitions.mjs` reconstructs each step's historical entry and exit
and describes operations in the owning subsystem. Its state labels are presentation
concepts, not shared wire contracts. Provisioning starts from an illustrative target
whose prestate must be verified; no fresh-board qualification is implied. Later
authoring and publication alter management intent without claiming a device update.
The final step previews required execution work and leaves runtime unproven.
The builder generates `walkthrough-data.mjs` from an allowlist of existing public
fixtures and the authoritative catalog. It copies fixture bytes unchanged for
download. Specified records show those fixtures; deferred handoffs show conceptual
obligations, never an invented shared wire schema. Nothing is authenticated,
provisioned, enrolled or published by this client-side simulation. The recorded
fixture time is assumed; the browser does not assess current credential validity.

Run the behavior checks with Node.js 22 or newer:

```sh
node --test tests/test_walkthrough.mjs
```

They cover progression gates, the development block, all-or-nothing conflict
rejection, one durable acceptance across a lost response and retry, reset, state
continuity, external concurrent changes, and the distinction between management
intent and actual device assignment/runtime.
The Pages build workflow runs them before upload or deployment. Use the browser
to verify both page navigation and scenario interactions at desktop/mobile widths;
without JavaScript, the page links back to the complete static guide.

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
