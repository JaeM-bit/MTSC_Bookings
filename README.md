# Tennis Booking Analysis Portal

A Streamlit portal for reviewing and analysing sanitised tennis court booking data from an Excel workbook. It can run locally or on Streamlit Community Cloud.

## Features

- Upload an `.xlsx` or `.xlsm` booking workbook.
- Choose the worksheet and header row.
- Automatically map the approved booking fields, with manual mapping controls.
- Filter by court, booking category, date range and weekday.
- Apply secondary filters for time of day, booking type and membership status.
- View totals and charts for bookings by court, category and weekday.
- Inspect the filtered bookings in an interactive table.
- Use the same Milford club identity as the fixtures portal, with a mid-blue analytics theme.

## Install on macOS

You need Python 3.10 or later. To check your version, open Terminal and run:

```bash
python3 --version
```

In Terminal, move into this project folder:

```bash
cd TennisBookingAnalyticsPortal
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## Run the portal

Copy `2026 Booking Info.xlsx` into this folder if you want it to open automatically:

```text
tennis-booking-analytics-portal/
├── 2026 Booking Info.xlsx
├── app.py
├── requirements.txt
└── README.md
```

You can also upload the workbook from within the portal instead of copying it into the folder.

With the virtual environment activated, run:

```bash
streamlit run app.py
```

Streamlit will print a local address, normally `http://localhost:8501`, and should open it in your browser automatically. Stop the portal by pressing `Control-C` in Terminal.

For future runs:

```bash
cd TennisBookingAnalyticsPortal
source .venv/bin/activate
streamlit run app.py
```

## Workbook guidance

For privacy, the portal admits only these seven columns:

- Date
- Court(s)
- Booking category
- Duration
- Time of booking
- Booking type
- Membership status

Other workbook columns are discarded during import and cannot appear in mappings, filters, charts or the Bookings table.

Dates should be stored as Excel dates or recognisable date text. Times can be Excel times or common text formats such as `09:30` or `9:30 AM`.

## Share privately with GitHub

1. Create a private GitHub repository.
2. Add this project, including the sanitised `2026 Booking Info.xlsx` file.
3. Do not force-add files excluded by `.gitignore`; the virtual environment and Mac-only sync utilities are intentionally local.
4. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) and connect the private repository.
5. Create an app using `app.py` as the entrypoint.
6. Keep the app private and invite the intended viewers by email.

Streamlit Community Cloud will install the packages in `requirements.txt` automatically.

## Privacy and file safety

The app reads the workbook into memory and does not write changes back to it. The bundled workbook must remain sanitised before every GitHub update. The portal's strict allowlist is an additional safeguard, not a substitute for removing private data from the workbook itself.
