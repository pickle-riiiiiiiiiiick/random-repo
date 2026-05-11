# Piano City Milano 2026 — Event Finder

A mobile-first finder for the [Piano City Milano](https://pianocitymilano.it/) 2026 programme. 275 concerts across all Milan districts (Municipi 1–9 plus out-of-town), 14–17 May 2026.

## Features

- Filter by **day** (Thu preview / Fri / Sat / Sun)
- Filter by **genre** (sticky horizontal row — 19 genres)
- Filter by **district**, **category**, **time of day**, and **reservation** in a bottom sheet
- Full-text **search** over artist, venue, title
- **List** and **Map** views (Leaflet + CartoDB tiles)
- Click any pin or card to open a popup with **Reserve** (if required) and **Details** links

## Data

Events are scraped from `https://pianocitymilano.it/programma/`. Venue coordinates for ~93 venues missing from the official dataset were backfilled by hand.

## Local viewing

Open `index.html` directly in a browser — everything is inlined.
