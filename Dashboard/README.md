EcoBloom Unified Dashboard

This folder contains a minimal Flask app that serves a unified dashboard integrating the project's P2P, pest-detection and heat-stress UI pages.

How to run (Windows cmd.exe):

1. Create a virtual environment and activate it (optional but recommended):

    python -m venv .venv
    .\.venv\Scripts\activate

2. Install requirements:

    pip install -r requirements.txt

3. Run the app:

    python app.py

4. Open http://localhost:8080 in your browser.

Notes:
- The app serves the HTML files directly from the project attachments. If you change files in the original folders (`P2P-System`, `Pest-detection`, `heat_risk`), they will be reflected automatically.
- The `/api/summary` endpoint returns a small JSON with connected peers and alert mentions by scanning files in `P2P-System`.
