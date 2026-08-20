# SensaApp

A full-stack sensory-information platform that helps students understand campus environments before entering them.

[View the live demo](https://sensaapp.onrender.com)

> **Project status:** SensaApp is currently an independent demonstration project. It is not yet an official service of, or affiliated with, any university.

## About the Project

SensaApp displays recently reported sensory conditions for campus spaces, including noise, crowdedness, lighting, and temperature.

I developed the backend during summer 2026 after completing a FastAPI course, applying what I learned to a real accessibility challenge. I later connected it to a lightweight frontend and deployed the complete demonstration on Render.

The long-term goal is to develop SensaApp further through user feedback and future collaboration with universities.

## Features

* Browse universities and their campus locations
* View noise, crowdedness, lighting, and temperature scores
* See an overall sensory score and the age of the latest report
* Create a viewing account and securely log in
* Request a new update for an outdated location
* Allow approved ambassadors to submit sensory reports
* Route update requests to ambassadors assigned to the relevant university
* Automatically clear an update request after a new report is submitted
* Validate emails, sensory scores, IDs, and user input
* Protect administrative and ambassador actions using role-based authorization

## User Roles

| Role          | Capabilities                                                    |
| ------------- | --------------------------------------------------------------- |
| Viewer        | Browse sensory information and request location updates         |
| Ambassador    | Submit reports and view requests for their assigned university  |
| Administrator | Manage universities, locations, administrators, and ambassadors |

## Technology Stack

* **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
* **Authentication:** JWT bearer authentication and bcrypt password hashing
* **Database:** PostgreSQL or SQLite through SQLAlchemy
* **Frontend:** HTML, CSS, and JavaScript
* **Deployment:** Render

## How It Works

1. A user selects a university and campus location.
2. SensaApp displays the most recent sensory report for that location.
3. If the information is outdated, a logged-in viewer can request an update.
4. An assigned ambassador receives the request and submits a new report.

## Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/hamad-nabeel/SensaApp.git
cd SensaApp
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the environment

```bash
cp .env.example .env
```

Generate a secure JWT key:

```bash
openssl rand -hex 32
```

Place the generated value in `.env` as `SENSA_SECRET_KEY`.

| Variable           | Purpose                                               |
| ------------------ | ----------------------------------------------------- |
| `SENSA_SECRET_KEY` | Secret key used to sign JWT access tokens             |
| `DATABASE_URL`     | SQLAlchemy connection URL for SQLite or PostgreSQL    |
| `ENABLE_API_DOCS`  | Set to `true` to enable FastAPI documentation locally |

### 5. Start the application

```bash
uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

If API documentation is enabled, it is available at `http://127.0.0.1:8000/docs`.

## Main API Endpoints

| Method | Endpoint                       | Purpose                             |
| ------ | ------------------------------ | ----------------------------------- |
| `POST` | `/auth/new_account`            | Register a viewing account          |
| `POST` | `/auth/token`                  | Authenticate and receive a JWT      |
| `GET`  | `/users/universities`          | Retrieve universities               |
| `GET`  | `/users/universities/{id}`     | Retrieve campus locations           |
| `GET`  | `/users/get_location_report`   | Retrieve the latest sensory report  |
| `POST` | `/users/request_update`        | Request updated sensory information |
| `POST` | `/ambassadors/submit_report`   | Submit a new sensory report         |
| `GET`  | `/ambassadors/update_requests` | Retrieve pending update requests    |

## Initial Administrator Setup

When the database contains no administrators, the first administrator can be created through `POST /admin/create_admin`.

After the first administrator has been created, that endpoint requires authentication from an existing administrator.

## Project Structure

* `backend/` — FastAPI application, database models, authentication, and API routers
* `frontend/` — HTML, CSS, and JavaScript user interface
* `requirements.txt` — Python dependencies
* `.env.example` — Example environment configuration
* `runtime.txt` — Python runtime used for deployment

## Roadmap

* Gather feedback from students and university stakeholders
* Expand the number of supported campus locations
* Recruit and manage verified sensory ambassadors
* Conduct accessibility and usability testing
* Add automated backend tests and database migrations
* Develop a mobile-first version of SensaApp

## Author

Developed by [Hamad Nabeel](https://github.com/hamad-nabeel).
