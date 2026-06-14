
if [ -z "$1" ]; then
  echo "Usage: create-template.sh <template-name>"
  exit 1
fi

mkdir -p docker/$1
touch docker/$1/docker-compose.yml
touch docker/$1/.env.example

./venv/bin/python3 scripts/create-monitor.py "$1" "https://$1.lan.nathanryder.xyz/"