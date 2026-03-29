FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY servidor/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN useradd -m appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "servidor.main:app", "--host", "0.0.0.0", "--port", "8000"]
