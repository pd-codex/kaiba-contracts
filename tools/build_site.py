"""Build the dependency-free process guide and check its local/source links."""

from html import escape
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
REPOSITORY = "https://github.com/pd-codex/kaiba-contracts"
DETAILS = {
    "ProvisioningRecord": "contracts/provisioning-record.md",
    "DeviceBinding": "contracts/device-binding.md",
    "PublishRequest": "contracts/publication.md",
    "Publication": "contracts/publication.md",
}
FIXTURES = (
    "provisioning-development", "provisioning-production-candidate",
    "binding-staged", "binding-active", "publish-request", "publication",
)


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise ValueError(f"Duplicate HTML id: {attrs['id']}")
            self.ids.add(attrs["id"])
        for name in ("href", "src"):
            if name in attrs:
                self.links.append(attrs[name])


def build():
    version = (ROOT / "VERSION").read_text().strip()
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    source = f"{REPOSITORY}/blob/{revision}"
    rows = []
    catalog = {}
    specified = 0
    for line in (ROOT / "docs/catalog.md").read_text().splitlines():
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not line.startswith("| ") or len(cells) != 4:
            continue
        name, boundary, meaning, coverage = cells
        if coverage not in ("Specified", "Specified within Publication", "Deferred"):
            continue
        defined = coverage.startswith("Specified")
        specified += defined
        if defined != (name in DETAILS):
            raise ValueError(f"Update the process guide's detail links for {name}")
        target = DETAILS.get(name, "docs/catalog.md")
        catalog[name] = {"specified": defined, "url": f"{source}/{target}"}
        badge = "Specified" if defined else "Deferred"
        rows.append(
            f'<tr><th scope="row"><a href="{source}/{target}">{escape(name)}</a></th>'
            f'<td>{escape(boundary)}</td><td>{escape(meaning)}</td>'
            f'<td><span class="badge {"specified" if defined else "deferred"}">'
            f'{badge}</span></td></tr>'
        )
    if not rows:
        raise ValueError("No contracts found in docs/catalog.md")

    replacements = {
        "version": escape(version),
        "source": source,
        "revision": revision[:7],
        "catalog_rows": "\n".join(rows),
        "specified_count": str(specified),
        "deferred_count": str(len(rows) - specified),
    }
    OUTPUT.mkdir(exist_ok=True)
    pages = {}
    for template in (ROOT / "website").glob("*.html"):
        page = template.read_text()
        for key, value in replacements.items():
            page = page.replace("{{" + key + "}}", value)
        if re.search(r"\{\{.*?\}\}", page):
            raise ValueError(f"Unresolved template token in {template.name}")
        (OUTPUT / template.name).write_text(page)
        parser = Links()
        parser.feed(page)
        pages[template.name] = parser
    for pattern in ("*.css", "*.mjs"):
        for asset in (ROOT / "website").glob(pattern):
            (OUTPUT / asset.name).write_bytes(asset.read_bytes())
    fixtures = {}
    (OUTPUT / "fixtures").mkdir(exist_ok=True)
    for name in FIXTURES:
        raw = (ROOT / "examples/valid" / f"{name}.json").read_bytes()
        fixtures[name] = json.loads(raw)
        (OUTPUT / "fixtures" / f"{name}.json").write_bytes(raw)
    data = {"fixtures": fixtures, "catalog": catalog, "source": source, "version": version}
    (OUTPUT / "walkthrough-data.mjs").write_text(
        "// Generated from the repository's public, synthetic fixtures.\n"
        + "export default " + json.dumps(data, ensure_ascii=True) + ";\n"
    )
    (OUTPUT / ".nojekyll").write_text("")
    for filename, parser in pages.items():
        for link in parser.links:
            if link.startswith(source + "/"):
                path = unquote(urlsplit(link[len(source) + 1:]).path)
                if not (ROOT / path).is_file():
                    raise ValueError(f"Missing repository source: {link}")
            elif not urlsplit(link).scheme:
                url = urlsplit(link)
                if url.path.startswith("/"):
                    raise ValueError(f"Link escapes the Pages project subpath: {link}")
                target = unquote(url.path) or filename
                if not (OUTPUT / target).is_file():
                    raise ValueError(f"Missing site file: {link}")
                if url.fragment and (
                    target not in pages or url.fragment not in pages[target].ids
                ):
                    raise ValueError(f"Missing site anchor: {filename} → {link}")
    count = sum(len(parser.links) for parser in pages.values())
    print(f"Built {OUTPUT}: {len(pages)} pages, {len(rows)} contracts, {count} links checked.")


if __name__ == "__main__":
    build()
