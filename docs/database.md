# Database Guide

## Overview

The Health Registration System uses SQLite as its local database. The database file is stored in the project folder as `hrs.db`.

## Database file

- File name: `hrs.db`
- Location: project database directory
- Type: local SQLite database

## Tables

The application creates the following tables:

- `doctors`
- `patients`
- `visits`
- `tokens`

## Main purposes

- Store patient registration records
- Store doctor information
- Track visit history
- Generate token records for report preview flow

## Notes

- The database is local and does not require a server.
- The app initializes the database automatically when needed.
- Foreign keys are enabled for relational integrity.
