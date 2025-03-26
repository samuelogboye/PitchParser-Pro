import os
from pitch import create_app
from uuid import uuid4

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=True)