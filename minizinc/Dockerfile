FROM ubuntu:latest

RUN apt-get -y update
RUN apt-get -y install minizinc

RUN apt-get install -y python3

RUN apt install -y python3-pip
RUN pip3 install minizinc


COPY dzn /dzn
COPY mzn /mzn
COPY py /py



ENTRYPOINT [ "python3", "./py/M+QA_MiniZinc2Python.py"]

# HOW TO USE:
# Execute following commands in cmd in workdirectory where the Dockerfile is located:
# 1) To Create Image (downloads all required packages if not already installed)
# docker build -t <imagename>:<imagetag> .  # <- That point is important!
# 2) To Execute created image as container
# docker run --name <mycontainername> -t -i <imagename>:<imagetag>
# 3) To Remove all Created Container
# docker system prune


