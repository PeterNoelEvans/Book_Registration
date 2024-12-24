# Library Book Registration System

A simple Flask-based system for tracking book borrowing in a classroom setting. Students can borrow books, and teachers can track which books are currently borrowed, view borrowing history, and manage book reviews.

## Features

- Track student book borrowing
- View currently borrowed books
- View reading history for each student
- Book review management system
- Re-borrowing system for returned books
- Export unreturned books list
  - Excel format (.xlsx)
  - CSV format (.csv)
  - See [Export Documentation](docs/export_feature.md) for details
- Simple web interface
- Easy setup for new classrooms
- Reading statistics with visual charts

## Setup Requirements

- Python 3.x
- Flask (for web application)
- Pandas (for data export)
- Openpyxl (for Excel export)
- Chart.js (included via CDN for statistics)

## Quick Start

1. Clone the repository:

