FROM musedev/analyst:latest

ENV PYTHONPATH="/opt/biggroum/python/"
ENV GRAPHEXTRACTOR="/opt/fixrgraphextractor_2.12-0.1.0-one-jar.jar"
WORKDIR /opt
#RUN apt-get install -y wget python-pip
#RUN pip install nose requests
#RUN wget https://github.com/cuplv/FixrGraphExtractor/releases/download/v1.0-musedev/fixrgraphextractor_2.12-0.1.0-one-jar.jar
#RUN git clone https://github.com/cuplv/biggroum.git
#RUN cd biggroum && git checkout musedev_hackaton && git pull
ADD setup_docker.sh setup_docker.sh
RUN ./setup_docker.sh
