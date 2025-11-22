FROM python:3.11-slim

WORKDIR /app

COPY app.py /app/app.py

RUN pip install --no-cache-dir streamlit==1.36.0 requests==2.32.3

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
