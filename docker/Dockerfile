FROM ubuntu:16.04


################################################################################
# Install packages
#
# 1. openssh-server, gcc, make, sudo, cmake, apt-transport-https
# 2. Oracle Java Jdk 8
# 3. sbt
# 4. Android SDK
# 5. Python 2
# 6. Google protobuffer
# 7. Microsoft z3
#
################################################################################

# 1. openssh-server, gcc, make, sudo, cmake, apt-transport-https
RUN apt-get update
RUN apt-get install -y openssh-server gcc make sudo cmake apt-transport-https software-properties-common

# 2. Oracle Java Jdk 8
RUN \
  echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
  add-apt-repository -y ppa:webupd8team/java && \
  apt-get update && \
  apt-get install -y oracle-java8-installer && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf /var/cache/oracle-jdk7-installer

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle

# 3. sbt
RUN echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
RUN sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
RUN sudo apt-get update
RUN sudo apt-get install -y sbt

# 4. Android SDK

# 5. Python 2

# 6. Google protobuffer

# 7. Microsoft z3

################################################################################
# Set up user
################################################################################
RUN mkdir /var/run/sshd
RUN chmod 0755 /var/run/sshd
RUN useradd biggroum
RUN groupadd admin
RUN usermod -a -G admin biggroum


# overwrite this with 'CMD []' in a dependent Dockerfile
CMD ["/bin/bash"]

