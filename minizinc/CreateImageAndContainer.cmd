REM docker system prune -f
docker build -t minizinc:murmeltier .
docker kill minizinc_container
docker rm minizinc_container
docker run -t -i --name minizinc_container minizinc:murmeltier