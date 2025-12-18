## Why PDF?
A web-based dashboard is great for interactive discovery, but a PDF is the **"Artifact of Record."** It allows the customer to:
1. Print and review the numbers in isolation.
2. Attach the sizing results to an internal business case.
3. Share the findings with stakeholders who do not have access to the app.

## The `fpdf2` Logic
We use the `fpdf2` library because it is highly compatible with Python 3.12 and `uv`.
- **Layout:** We use a simple grid-based layout to ensure readability.
- **Dynamic Content:** The PDF function accepts variables calculated from the RVTools CSV, meaning every report is unique to the customer's data.

## Sales Best Practice
Always generate the PDF **at the end of the demo** after you have tuned the consolidation sliders and sizing assumptions with the customer. This ensures they feel "ownership" of the numbers in the final document.
