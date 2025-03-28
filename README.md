# PitchParser Pro - Document Parsing API

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
- **State Management**: React Context or Redux (optional)

## Prerequisites
- Docker and Docker Compose installed on your machine.
- Node.js and npm/yarn for frontend development (if running frontend separately).

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pitchparser-pro.git
   cd pitchparser-pro
   ```

2.  Run with Docker:
    
    ```bash
    docker compose up --build
    ```

## API Endpoints


| Method | Endpoint  | Description                      |
|--------|----------|----------------------------------|
| POST   | /upload  | Upload a PDF/PPTX file for parsing |

## Testing

```bash
curl -X POST -F "file=@pitch_deck.pdf" http://localhost:5000/upload
```
## Tech Stack

-   **Backend**: Flask, Celery (async processing)
    
-   **Database**: PostgreSQL
    
-   **Cache**: Redis
    
-   **Queue**: RabbitMQ
    
-   **Parsing**: PyPDF2, python-pptx
    

## **Why This Solution Stands Out**
✅ **Scalable Architecture** (Docker, Celery, Redis)  
✅ **Robust Error Handling** (File validation, async retries)  
✅ **Extensible Parsing** (Easy to add new document types)  
✅ **Clear Documentation** (README, API specs, Swagger Doc)