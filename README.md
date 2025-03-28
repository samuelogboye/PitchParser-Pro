
# PitchParser Pro

## Overview
This project is a web application designed to parse and process uploaded pitch deck documents (PDF or PowerPoint). It includes a backend built with Flask, Celery, Redis, RabbitMQ, and Docker, and a frontend developed with React, TypeScript, and Tailwind CSS. Users can register, log in, upload documents, and view parsed data in a dashboard.

## Features
- **User Authentication**: Register and login functionality.
- **File Upload**: Upload PDF or PowerPoint files for parsing.
- **Data Parsing**: Extract slide titles, text content, and metadata from documents.
- **Data Storage**: Store parsed data in a PostgreSQL database.
- **Dashboard**: Display parsed data in a table format.
- **Error Handling**: Robust handling of unsupported formats, corrupted files, etc.
- **Asynchronous Processing**: Use Celery and RabbitMQ for background tasks.
- **Caching**: Redis for caching frequently accessed data.

## Technologies Used
### Backend
- **Framework**: Flask (Python)
- **Task Queue**: Celery
- **Message Broker**: RabbitMQ
- **Caching**: Redis
- **Database**: PostgreSQL
- **File Parsing**: PyPDF2 (PDF), Apache POI (PPTX)
- **Containerization**: Docker

### Frontend
- **Framework**: React (TypeScript)
- **Styling**: Tailwind CSS
- **State Management**: React Context 

## Prerequisites
- Docker and Docker Compose installed on your machine.
- Node.js and npm/yarn for frontend development (if running frontend separately).

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Backend Setup

#### Environment Variables

Create a  `.env`  file in the  `backend`  directory with the following variables:

```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://postgres:postgres@db:5432/pitch_deck_db
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=amqp://rabbitmq:5672
SECRET_KEY=your-secret-key
```
You can also create from .env.example file

#### Run with Docker

From the project root, run:

```bash
docker-compose up --build
```

This will start the following services:

-   Flask backend (`api`)
    
-   PostgreSQL database (`db`)
    
-   Redis (`redis`)
    
-   RabbitMQ (`rabbitmq`)
    
-   Celery worker (`celery`)
    

### 3. Frontend Setup

Navigate to the  `frontend`  directory here https://github.com/samuelogboye/PitchParser-Frontend:

```bash
cd frontend

#### Install Dependencies

```bash
npm install
```
#### Run the Frontend

```bash
npm run dev
```
The frontend will be available at  `http://localhost:5173`.

## API Routes

### Authentication

-   **POST /api/v1/auth/register**: Register a new user.
    
    -   Request Body:
        
        ```json
        {
          "email": "string",
          "password": "string"
        }
        ```
        
-   **POST /api/v1/auth/login**: Log in an existing user.
    
    -   Request Body:
        
        ```json
        {
          "email": "string",
          "password": "string"
        }
        ```
        

### Document Upload and Parsing

-   **POST /api/v1/parser/upload**: Upload a pitch deck file (PDF or PPTX).
    
    -   Headers:  `Authorization: Bearer <token>`
        
    -   Form Data:  `file`  (the document to upload).
        
-   **GET  /api/v1/parser/pitch-decks**: Retrieve all parsed documents for the logged-in user.
    
    -   Headers:  `Authorization: Bearer <token>`
        

## Testing

### Backend Tests

To run unit tests for the backend:

```bash
docker-compose run api python -m pytest
```



## Additional Notes

-   The Celery worker processes file uploads asynchronously.
    
-   Redis caches frequently accessed data to improve performance.
    
-   PostgreSQL is used for persistent data storage.
    
-   Ensure all services are running (`api`,  `db`,  `redis`,  `rabbitmq`,  `celery`) before testing.
    

## Troubleshooting

-   **Docker Issues**: Ensure Docker is running and ports are not occupied.
    
-   **Database Errors**: Verify the PostgreSQL service is up and the  `.env`  file is correctly configured.
    

## Contact

For questions or issues, please contact:  [Samuel Ogboye](https://mailto:ogboyesam@gmail.com/).