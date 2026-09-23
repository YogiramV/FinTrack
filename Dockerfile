FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["sh", "-c", "python stream/kafka_setup.py && (python -m stream.kafka_consumer &) && exec streamlit run main.py --server.address=0.0.0.0"]