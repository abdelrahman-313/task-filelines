FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY . /app

# copy entrypoint to a path NOT covered by the bind mount
COPY entrypoint.sh /docker/entrypoint.sh
RUN sed -i 's/\r$//' /docker/entrypoint.sh && chmod +x /docker/entrypoint.sh

ENTRYPOINT ["/docker/entrypoint.sh"]