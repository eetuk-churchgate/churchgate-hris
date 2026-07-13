"""
Patch Streamlit's served index.html with real <title> + Open Graph / Twitter
meta tags so link-preview scrapers (WhatsApp, Slack, iMessage, Twitter, etc.)
show Churchgate branding instead of the default "Streamlit" card.

Streamlit's index.html lives inside the installed package (site-packages), which
is rebuilt on every deploy — so this runs at container startup (see start.sh).
Idempotent: re-running is a no-op once patched.
"""
import os
import sys
import streamlit

OG_IMAGE = "https://raw.githubusercontent.com/eetuk-churchgate/churchgate-hris/main/churchgate_logo.png"
SITE_URL = "https://hris.churchgate.com"
TITLE = "Churchgate Group HRIS"
DESCRIPTION = "Enterprise HR portal for Churchgate Group — employee management, performance appraisals, and analytics."
MARKER = "<!-- churchgate-meta -->"

META_BLOCK = f"""<title>{TITLE}</title>
    {MARKER}
    <meta name="description" content="{DESCRIPTION}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="{TITLE}" />
    <meta property="og:title" content="{TITLE}" />
    <meta property="og:description" content="{DESCRIPTION}" />
    <meta property="og:image" content="{OG_IMAGE}" />
    <meta property="og:url" content="{SITE_URL}" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="{TITLE}" />
    <meta name="twitter:description" content="{DESCRIPTION}" />
    <meta name="twitter:image" content="{OG_IMAGE}" />"""


def main() -> int:
    index_path = os.path.join(os.path.dirname(streamlit.__file__), "static", "index.html")
    if not os.path.exists(index_path):
        print(f"[patch_meta] index.html not found at {index_path}; skipping.")
        return 0

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    if MARKER in html:
        print("[patch_meta] already patched; nothing to do.")
        return 0

    if "<title>Streamlit</title>" in html:
        html = html.replace("<title>Streamlit</title>", META_BLOCK, 1)
    elif "</head>" in html:
        # Fallback if Streamlit changes its default <title>.
        html = html.replace("</head>", META_BLOCK + "\n</head>", 1)
    else:
        print("[patch_meta] no injection point found; skipping.")
        return 0

    try:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[patch_meta] injected OG/meta tags into {index_path}")
    except OSError as e:
        # Non-fatal: the app still runs, just without the rich preview.
        print(f"[patch_meta] could not write index.html ({e}); continuing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
