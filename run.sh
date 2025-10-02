docker build . -t oomf-dev --build-arg GIT_COMMIT_HASH=$(git rev-parse HEAD)
docker rm oomf-dev
docker run --name oomf-dev --env-file .env oomf-dev
