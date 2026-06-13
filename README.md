# Event Registration and Check-In System

A django Django-based web application for managing events, user registration, and self check-in using a QR code and a unique email or phone number. It is designed for real-world use in conferences, workshops, trainings, and similar events.

## Overview

###### The system allows users to:

  * View available events
  * Register for an event using their name, email,  and phone number
  * Check in at the event by scanning a QR code and entering their details

## How It Works
### 1. Event Creation

Events are created by the admin with details such as title, location, date, and capacity of the event.

### 2. Registration

  -- Users register for an event by filling out a form. 
  
  ##### The system ensures:

  -- That a user cannot register twice using the same email for the same event

  -- That a user cannot register twice using the same phone number for the same event

  -- That a user cannot check-in twice using the same phone number for the same event

  -- That a user cannot check-in twice using the same email for the same event

### 3. Check-In QR Code

Each event has a unique check-in URL:

  `/checkin/<event_uuid>/`

This URL is converted into a QR code and placed at the event entrance.

### 4. Check-In Process

When users arrive at the event:

  * They scan the QR code
  * They are taken to the check-in page
  * They enter their email or phone number
  * The system verifies their registration
  * If valid, they are marked as checked in
  * Each user can only check in once.

## Features
  * Events listing page
  * Event registration system
  * Duplicate registration prevention
  * QR code-based event check-in
  * Self-service attendance tracking
  * Check-in timestamp recording
  * Simple and responsive UI using Bootstrap

## Technology Stack
  * Python
  * Django
  * SQLite
  * HTML, CSS and Bootstrap
  * JavaScript 
  * qrcode library

## Installation
### 1. Clone the repository
  `git clone https://github.com/yourusername/event-system.git`

  `cd event-system`

### 2. Create a virtual environment
  `python -m venv venv`

Activate the virtual environment:

  `venv\Scripts\activate`

### 3. Install dependencies
  `pip install -r requirements.txt`

### 4. Run migrations
  `python manage.py makemigrations`

  `python manage.py migrate`

### 5. Start the server
  `python manage.py runserver`


## Usage Flow
 1. Create an event
 2. Users register for the event
 3. System generates a check-in link
 4. QR code is printed and placed at the venue
 5. Users scan the QR code and check in

## Notes

Each event has a unique UUID used for check-in

Duplicate registrations are prevented at database level

Check-in is restricted to one time per user

The system is designed for simplicity and real-time event use

The events are fetched differently, past and upcoming

## Future Improvements

* Admin dashboard for attendance analytics
* Export attendance to CSV/Excel
* Email confirmation after registration
* Login system for users
* User Roles to manage events
* Alerts during registration and event reminder