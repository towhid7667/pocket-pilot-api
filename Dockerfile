FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pytest pytest-asyncio
COPY app/ app/  
COPY tests/ tests/  
CMD ["pytest", "tests", "--asyncio-mode=auto", "-v"]