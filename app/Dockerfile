# FROM python:3.9

# RUN mkdir /fastapi_app

# WORKDIR /fastapi_app

# COPY requirements.txt .

# RUN pip install -r requirements.txt

# COPY . .

# RUN chmod a+x docker/*.sh

# WORKDIR app/src

# CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000


# FROM python:3.9

# RUN mkdir /fastapi_app

# WORKDIR /app

# COPY requirements.txt .

# RUN pip install -r requirements.txt

# COPY . .

# RUN chmod a+x docker/*.sh

# # Don't change WORKDIR if your main.py is in the root
# # Or set it to where your main.py actually is
# # WORKDIR /fastapi_app/app/src

# # Updated CMD to use the correct module path
# CMD ["gunicorn", "app.src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

FROM python:3.9

WORKDIR /app

# Install dependencies first for caching
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN echo zalupa

# Copy the entire project
COPY . .

# Make sure Python can find your modules
# ENV PYTHONPATH=/app

# Install the package in development mode
# RUN pip install -e .

CMD ["gunicorn", "tasks.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]