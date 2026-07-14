# Event Ticket Booking System

## Project Overview

This project is a web-based Event Ticket Booking System for a small event management company called Evently.

The system will help staff manage events and customer bookings in one place.

## Main Features

- Create events
- View events
- Update events
- Delete events
- Search events
- Create customer bookings
- Track available tickets

## Technologies Used

- Python
- Flask
- MongoDB Atlas
- HTML
- CSS
- JavaScript
- GitHub

## System Architecture

```text
Frontend
HTML, CSS, JavaScript
        |
        v
Flask REST API
        |
        v
MongoDB Atlas


## Current Backend

### System

- `GET /`
- `GET /api/health`
- `GET /api/database-health`

### Events

- `GET /api/events`
- `GET /api/events/<event_id>`
- `POST /api/events`
- `PUT /api/events/<event_id>`
- `DELETE /api/events/<event_id>`

### Bookings

- `GET /api/bookings`
- `GET /api/bookings/<booking_id>`
- `POST /api/bookings`
- `PUT /api/bookings/<booking_id>/cancel`

## Current Progress

- [x] GitHub repository created
- [x] Initial project structure created
- [x] Basic documentation added
- [x] Flask backend created
- [x] Python dependencies
- [x] Environment variables configured
- [x] Application configuration module
- [x] MongoDB connection
- [x] Event input validation
- [x] Create event API
- [x] Get all events API
- [x] Get single event API
- [x] Update event API
- [x] Delete event API
- [x] Event CRUD
- [x] Booking input validation
- [x] Create booking API
- [x] Get all bookings API
- [x] Get single booking API
- [x] Cancel booking API
- [x] Booking functionality
- [x] Frontend HTML structure
- [x] Responsive frontend styling
- [x] Frontend API integration
- [x] Frontend integration
- [x] End-to-end testing

## AI and External Assistance

Generative AI was used for planning, technical guidance, debugging and documentation review. All suggestions were reviewed and adapted before use.

## Running the Project

### Backend

```powershell
.\.venv\Scripts\Activate.ps1
python backend\app.py

### Backend runs at:

http://127.0.0.1:5000


## Testing

The project includes unit tests for input validation and integration tests for the Flask API.

Run all tests using:

```powershell
python -m pytest tests -v


## Lecturer Access

The project can be downloaded or cloned from this public GitHub repository.

### Setup

```powershell
git clone https://github.com/UsamaRafiq853/event-ticket-booking-system.git
cd event-ticket-booking-system
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
