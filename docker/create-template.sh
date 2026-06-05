

if [ -z "$1" ]; then
  echo "Usage: create-template.sh <template-name>"
  exit 1
fi

mkdir $1
touch $1/docker-compose.yml
touch $1/.env.example