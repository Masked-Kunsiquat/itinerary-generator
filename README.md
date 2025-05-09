# 🧳 Surmai Itinerary Generator

A web-based tool for rendering beautiful, print-ready trip itineraries from Surmai's `trip.json` exports using customizable Jinja2 HTML templates. Optionally supports PDF generation using [Gotenberg](https://github.com/gotenberg/gotenberg).

![CI](https://github.com/Masked-Kunsiquat/itinerary-generator/actions/workflows/test.yml/badge.svg)

---

## 🧾 About Surmai

This project was inspired by [Surmai](https://github.com/rohitkumbhar/surmai) — an alpha-stage personal/family travel organizer built by [@rohitkumbhar](https://github.com/rohitkumbhar). Surmai aims to:

* Allow collaborative planning between multiple people
* Provide easy access to artifacts throughout the trip
* Keep travel data private

This tool provides a way to export and beautify Surmai trip plans.

> **NOTE:** Surmai is in active development. Please report bugs and suggestions to its [GitHub Issues page](https://github.com/rohitkumbhar/surmai/issues).

---

## ✨ Features

* Upload a Surmai-style `trip.json` export
* Upload your custom Bootstrap 5+ HTML template (Jinja2-compatible)
* Automatically uses a default template if none is provided
* View & download rendered HTML
* Optionally generate and download a PDF via Gotenberg
* Includes power-user documentation and downloadable examples

---

## 🚀 Quick Start

### 1. Clone the Repo

```bash
git clone https://github.com/Masked-Kunsiquat/itinerary-generator.git
cd itinerary-generator
```

### 2. Run via Docker Compose

```bash
docker-compose up --build
```

Then open your browser and visit: [http://localhost:5000](http://localhost:5000)

---

## 📁 Upload Details

You’ll need:

* `trip.json` – from Surmai's export
* `template.html` – your HTML layout using Jinja2 placeholders like `{{ trip_name }}`, `{% for day in days %}`, etc.

If no template is uploaded, `default-template.html` will be used.

---

## 🖨️ PDF Generation

If "Generate PDF" is checked in the UI:

* The rendered HTML is sent to Gotenberg (via internal Docker)
* A fully print-ready PDF is returned for download

---

## 🧑‍💻 Power User Guide: Theming & Templating

### 🧱 Common Variables

```jinja2
{{ trip_name }}
{{ start_date }}
{{ end_date }}
{{ trip_notes | safe }}

{% for day in days %}
  {{ day.date }}
  {{ day.events }}
  {{ day.lodging_banner }}
{% endfor %}
```

### 🧩 Custom CSS

Reference your custom CSS file like so:

```html
<link rel="stylesheet" href="/static/custom.css">
```

Place your `custom.css` inside the `/static` folder before building or serving the app.

### 🖼️ Reusable Class Names (Semantic Hooks)

| Class              | Purpose                                              |
| ------------------ | ---------------------------------------------------- |
| `.itinerary-day`   | Wraps each day block                                 |
| `.event-row`       | Each timeline entry (flights, check-ins, activities) |
| `.lodging-note`    | Subtle banner for current lodging                    |
| `.summary-section` | Two-column footer section                            |

---

## 🧪 Sample Files

To help you get started quickly:

* [`trip.sample.json`](./static/trip.sample.json) — A fictional 5-day trip with transport, lodging, and activities
* [`template.sample.html`](./static/template.sample.html) — A minimal Jinja2 + Bootstrap 5 template

Both are also downloadable from the UI.

---

## 🛠 Development Mode

Run without Docker:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## 📦 Repo Structure

```
.
├── Dockerfile
├── docker-compose.yaml
├── app.py                  # Flask web UI
├── generate_itinerary.py   # Jinja2 rendering + PDF logic
├── requirements.txt
├── default-template.html   # Used if no custom template is uploaded
├── static/
│   ├── trip.sample.json
│   ├── template.sample.html
│   └── (optional custom.css)
├── templates/
│   └── form.html           # Main upload form
└── .gitignore / .dockerignore
```

---

## 🔐 Notes

* Flask runs in development mode — suitable for local-only use
* Gotenberg runs inside Docker and communicates via `http://gotenberg:3000`
* All rendering happens server-side for PDF compatibility

---

## 💡 Future Ideas
This project was designed for simplicity, but power users or future contributors may want to explore enhancements like:

- 🌓 Theme switcher – Optional dark mode toggle (device preference detection was considered)

- 🔍 Template preview – Show a live HTML preview or thumbnail of selected template

- 🖼 UI polish – Add branding, logos, or customizable styles per user/team

- 🧪 Validation/linting – Warn users if uploaded templates are missing expected variables

- 💾 Local storage/cache – Persist previously used templates or inputs for convenience

- 🧱 Component-based templating – Support reusable partials or layout variants (e.g. day-card.html)

- 📄 Multiple templates – Let users pick from predefined themes/styles

- 🔐 Authentication – Useful for team deployments or protecting sensitive trip data

> Contributions welcome! Or fork this and make it your own ✨
---
## 📄 License

MIT — free to use and adapt. Attribution welcome.

---

## 🙋‍♂️ Author

Built by **Masked-Kunsiquat** (with help from ChatGPT).
Inspired by the goals of the [Surmai](https://github.com/rohitkumbhar/surmai) project.
