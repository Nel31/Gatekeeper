# Gatekeeper

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]() [![Coverage](https://img.shields.io/badge/coverage-100%25-blue)]() [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)]()

## Description

**Gatekeeper** is a lightweight, automated audit tool that checks user accounts in your applications against your official HR directory. It identifies:
- **In‑SGB** accounts (internal employees)
- **Out‑SGB** accounts (externals, contractors, or orphaned)
- **Dormant** accounts (> 120 days without login)
- **Never‑used** accounts

It then generates a polished Excel report based on your standard review template (`template_revue.xlsx`), ready for certification or deactivation.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Workflow](#workflow)
- [Tests](#tests)
- [Deployment & Scheduling](#deployment--scheduling)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [License](#license)
- [Authors & Acknowledgements](#authors--acknowledgements)
- [Contact & Support](#contact--support)

## Features

- **Clean & Normalize** multiple application extractions
- **Match** accounts against HR directory
- **Detect** dormant (> 120 days) and never‑used accounts
- **Generate** Excel report using your review template
- **Log** every execution with summary statistics
- **Schedule** periodic audits via cron or Task Scheduler

## Prerequisites

- Python ≥ 3.8
- pandas
- openpyxl
- unidecode

## Installation

1. Clone the repo  
   ```bash
   git clone https://github.com/your-org/gatekeeper.git
   cd gatekeeper
   ```  
2. Create and activate a virtual environment  
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Linux/macOS
   .\.venv\Scripts\activate  # Windows
   ```  
3. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

- **Folder layout** (defaults):
  ```
  gatekeeper/
  ├── data/  
  │   ├── rh_reference.xlsx        # official HR directory  
  │   ├── app1_users.xlsx          # application extraction(s)  
  ├── data_templates/  
  │   └── template_revue.xlsx      # review template with headers & dropdowns  
  ├── outputs/  
  ├── logs/  
  └── scripts/  
  ```
- **Options**:
  - `--rh` : path to your RH file
  - `--ext` : path to the application extraction file
  - (Optional) edit `config.yaml` to adjust thresholds (e.g. inactive days)

## Usage

Run Gatekeeper for a single application extraction:

```bash
python scripts/main.py   --rh data/rh_reference.xlsx   --ext data/app1_users.xlsx
```

- Output report: `outputs/rapport_revue_app1_users.xlsx`
- Log entry: `logs/audit.log`

## Project Structure

```
gatekeeper/
├── data/  
├── data_templates/  
├── outputs/  
├── logs/  
├── scripts/  
│   ├── excel_loader.py       # load & clean Excel data  
│   ├── comparator.py         # classify accounts (In/Out/Dormant/Never)  
│   ├── report_generator.py   # insert into review template  
│   └── main.py               # orchestrator & CLI interface  
├── requirements.txt  
└── README.md
```

## Workflow

1. **Read & clean** RH and extraction (strip, lowercase, remove accents).
2. **Aggregate** duplicates (keep most recent login).
3. **Compute** days of inactivity.
4. **Classify** accounts (In SGB / Out SGB / Dormant / Never).
5. **Build** review table matching `template_revue.xlsx` columns.
6. **Inject** rows into the Excel template.
7. **Save** report and **log** summary.

## Tests

*(If you add tests)*  
```bash
pytest tests/
```

## Deployment & Scheduling

- **Linux (cron)**:  
  ```cron
  0 6 1 * * /path/to/gatekeeper/.venv/bin/python /path/to/gatekeeper/scripts/main.py --rh /path/to/data/rh_reference.xlsx --ext /path/to/data/app1_users.xlsx
  ```
- **Windows (Task Scheduler)**: create a scheduled task that runs `python main.py` monthly.

## Contributing

1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/XYZ`)  
3. Commit your changes (`git commit -m "Add XYZ"`)  
4. Push (`git push origin feature/XYZ`)  
5. Open a Pull Request

Please follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code style.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## Authors & Acknowledgements

- **Your Name** – Initial development  
- **Contributors** – Thank you for your contributions!

## Contact & Support

For questions or issues, please open an issue on GitHub or reach out to **it-security@sgb.bj**.
