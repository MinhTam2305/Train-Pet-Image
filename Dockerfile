FROM python:3.11-slim
WORKDIR /app

# copy only requirements first for better layer caching
COPY requirements.txt ./
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LIGHT_MODE=1
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# copy app sources
COPY . /app

# build lightweight features at image build time (optional)
# keep this non-fatal so image build doesn't fail if data is missing
RUN python build_features_light.py || true

EXPOSE 5000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
