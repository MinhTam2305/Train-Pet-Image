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
# Force rebuild even if file exists since data/ might be new
RUN python build_features_light.py

EXPOSE 5000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
