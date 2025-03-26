# PitchParser Pro - Document Parsing API

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