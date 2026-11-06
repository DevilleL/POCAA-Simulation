# Relais de pilotage + robot simulé (sans écran), pour un hébergement permanent (Coolify sur le Legion).
# Les dépendances graphiques (pygame, matplotlib) ne servent qu'aux simulations locales : pas installées ici.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN pip install --no-cache-dir "fastapi>=0.110" "uvicorn[standard]>=0.29" "websockets>=12.0"
COPY src ./src
COPY web_control ./web_control
COPY deploy/start.sh ./start.sh
RUN useradd -r -u 10001 pocaa && chown -R pocaa /app
USER pocaa
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1
CMD ["./start.sh"]
