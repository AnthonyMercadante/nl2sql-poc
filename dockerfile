FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV HF_HOME=/app/.cache/huggingface
CMD ["python", "-m", "app.ui.interface"]
