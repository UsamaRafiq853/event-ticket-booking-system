# Event Ticket Booking System

## Project Overview

This project is an Event Ticket Booking System for a small event management company called Evently.

The purpose of the system is to help the company manage events and customer bookings in one place. Staff members will be able to add new events, view event details, update information and remove cancelled events.

The system will also allow customer booking details to be stored and managed.

## Selected Organisation

The selected organisation for this project is Evently.

Evently is a small event management company that organises workshops, conferences, music events and community events.

At the moment, the company needs a simple information system to manage event details and ticket bookings. The proposed system will reduce manual work and make it easier to find and update information.

## Problem Statement

Managing events and ticket bookings manually can create different problems.

Some common problems are:

- Event information may be incomplete
- Booking details may be entered incorrectly
- Staff may find it difficult to check ticket availability
- Duplicate records may be created
- Cancelled events may not be updated properly
- Searching for old bookings may take time
- The company may accidentally accept more bookings than available tickets

The Event Ticket Booking System will provide a basic solution to these problems.

## Project Objectives

The main objectives of this project are:

- Create a simple web-based information system
- Store event information in MongoDB Atlas
- Store customer booking information
- Add new event records
- View existing event records
- Update event information
- Delete event records
- Search for events
- Track available tickets
- Validate user input
- Use API calls between the frontend and backend
- Test the main system functions

## Main Features

The planned features of the system are:

- Create events
- View events
- Edit events
- Delete events
- Search events
- Create customer bookings
- View booking records
- Track ticket availability
- Display validation messages
- Store data in MongoDB Atlas

## Technologies Used

The following technologies will be used:

- Python
- Flask
- MongoDB Atlas
- PyMongo
- HTML
- CSS
- JavaScript
- Git
- GitHub

## System Architecture

The frontend will be developed using HTML, CSS and JavaScript.

JavaScript will send HTTP requests to the Flask backend using the Fetch API.

The Flask backend will process the requests and perform database operations using MongoDB Atlas.

```text
Frontend
HTML, CSS and JavaScript
          |
          | HTTP requests and JSON
          v
Flask REST API
          |
          | PyMongo
          v
MongoDB Atlas
