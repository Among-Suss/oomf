docker build . -t oomf --build-arg GET_COMMIT_HASH=$(git rev-parse HEAD)
docker rm oomf
docker run --name oomf --env-file .env oomf
