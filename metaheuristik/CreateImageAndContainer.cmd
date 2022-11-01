REM docker system prune -f
docker build -t metaheuristic:fischotter .
docker kill rechenstudie_container
docker rm rechenstudie_container
docker run -t -i --name rechenstudie_container -v "%cd%/figures":/metaheuristik/figures metaheuristic:fischotter