iris-fastapi/
├── api/
│   └── main.py              # FastAPI app with /predict endpoint
├── Dockerfile               # Dockerfile to containerize the app
├── requirements.txt         # Python dependencies
└── README.md                # Optional: project overview and usage


api/main.py: Contains the FastAPI code that loads the model and serves predictions.
Dockerfile: Uses Python 3.9, installs dependencies, and runs the app with Uvicorn.
requirements.txt: Lists fastapi, uvicorn, and scikit-learn.
README.md: (Optional) Add instructions for building, running, and using the API.
