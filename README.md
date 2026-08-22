# MTSC Booking Analytics Portal

A static booking analytics portal for Milford Tennis & Squash Club. It uses the same deployment approach as the fixtures portal: HTML, CSS, JavaScript, JSON data, GitHub and GitHub Pages.

## Portal files

- `index.html` — public analytics portal.
- `publisher.html` — local workbook-to-JSON publishing page.
- `app.js` — filters, calculations, charts, table and pagination.
- `publisher.js` — sanitised Excel import and JSON download.
- `data/bookings.json` — data displayed by the portal.
- `2026 Booking Info.xlsx` — sanitised source workbook retained for local updating.

## Preview locally

Double-click `Preview Portal.command`. The portal opens at:

`http://127.0.0.1:8766/`

Keep the Terminal window open while previewing. Press Control-C to stop it.

## Update the booking data

1. Start the local preview.
2. Open `http://127.0.0.1:8766/publisher.html`.
3. Choose the sanitised `.xlsx` or `.xlsm` workbook.
4. Confirm the record count and download `bookings.json`.
5. Replace `data/bookings.json` with the downloaded file.
6. Commit and push the change using GitHub Desktop.

The publisher exports only these approved fields:

- Date
- Court(s)
- Booking category
- Duration
- Time of booking
- Booking type
- Membership status

## GitHub Pages

In the repository settings, set Pages to deploy from the `main` branch and root folder. The portal will then be available at:

`https://jaem-bit.github.io/MTSC_Bookings/`

The publisher page is intended as a local tool. The bundled workbook and JSON must remain sanitised because a standard GitHub Pages site is public.
