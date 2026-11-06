#!/bin/sh
# Lance le relais ET le robot simulé dans le même conteneur (hébergement permanent sur le Legion).
#  - relais    : uvicorn web_control.relay:app sur le port 8000
#  - robot     : web_control.robot_client, sans écran, reconnecté automatiquement
#                si le relais redémarre ou si la connexion tombe.
# Variables : PILOT_TOKEN (obligatoire en production), POCAA_ROOM (défaut demo-classroom).
set -eu
: "${PILOT_TOKEN:?PILOT_TOKEN manquant}"
ROOM="${POCAA_ROOM:-demo-classroom}"

uvicorn web_control.relay:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*' --no-access-log &
RELAY=$!
trap 'kill $RELAY 2>/dev/null; exit 0' TERM INT

# Attendre que le relais réponde
for i in $(seq 1 30); do
  python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=1)" 2>/dev/null && break
  sleep 1
done

(
  while kill -0 $RELAY 2>/dev/null; do
    python -m web_control.robot_client --url ws://127.0.0.1:8000 --room "$ROOM" --token "$PILOT_TOKEN" || true
    echo "[sim] déconnecté du relais, nouvelle tentative dans 3 s"
    sleep 3
  done
) &

wait $RELAY
