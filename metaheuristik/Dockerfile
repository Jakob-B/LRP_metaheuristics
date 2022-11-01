#FROM ubuntu:latest

FROM python:3.8

WORKDIR /metaheuristik

RUN pip3 install --upgrade pip

COPY instances /metaheuristik/instances
COPY marinakis /metaheuristik/marinakis
COPY quinteroaraujo /metaheuristik/quinteroaraujo
COPY figures /metaheuristik/figures
COPY metaheuristicSolver.py /

RUN pip3 install numpy
RUN pip3 install typing
RUN pip3 install networkx
RUN pip3 install matplotlib
RUN pip3 install tqdm

ENV PYTHONPATH "${PYTHONPATH}:/"

#CMD ["cd"]
#CMD [ "python3", "./minizincTest2.py" ]
#ENTRYPOINT [ "python3", "/metaheuristik/quinteroaraujo/code/simils.py"]
#ENTRYPOINT [ "python3", "/metaheuristik/marinakis/code2/GLCENTPSO_Control.py"]
ENTRYPOINT [ "python3", "../metaheuristicSolver.py"]
#ENTRYPOINT [ "python3","-m", "metaheuristik.quinteroaraujo.code.simils"]
#CMD [ "python3", "./M+QA_MiniZinc2Python.py" ]
# in /: python -m metheuristik.quinteroaraujo.code.simils
# oder in /metaheuristik/quinteroaraujo/code: python simils.py

# HOW TO USE:
# Execute following commands in cmd in workdirectory where the Dockerfile is located:
# 1) To Create Image (downloads all required packages if not already installed)
# docker build -t <imagename>:<imagetag> .  # <- That point is important!
# 2) To Execute created image as container
# docker run --name <mycontainername> -t -i <imagename>:<imagetag>
# 3) To Remove all Created Container
# docker system prune


#docker run -t -i --name donnerstag1 -v "%cd%/figures":/metaheuristik/figures metaheuristik:gnu