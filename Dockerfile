
FROM python:3.10-alpine
WORKDIR app/
COPY . .
RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip pip3 install -r requirements.txt
CMD ["sh", "-c", "uvicorn web.app:app --host 0.0.0.0 --port 8000 & python3 main.py"]



