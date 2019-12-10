FROM ubuntu:16.04


################################################################################
# Install packages
#
# 1. openssh-server, gcc, make, sudo, cmake, apt-transport-https
# 2. OpenJdk 8
# 3. sbt
# 4. Python 2
# 5. Google protobuffer
# 6. Microsoft z3
# 7. Android SDK
#
################################################################################

# 1. openssh-server, gcc, make, sudo, cmake, apt-transport-https
RUN apt-get update
RUN apt-get install -y openssh-server gcc make sudo cmake apt-transport-https software-properties-common binutils g++

# 2. OpenJdk 8
RUN sudo apt-get install -y openjdk-8-jdk

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64

# 3. sbt
RUN echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
RUN sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
RUN sudo apt-get update
RUN sudo apt-get install -y sbt


# 4. Python 2
RUN sudo apt-get install -y python
RUN sudo apt-get install -y python-pip
RUN sudo pip install protobuf

# 5. Google protobuffer
RUN sudo apt-get install -y curl unzip autoconf automake libtool
RUN curl -OL https://github.com/google/protobuf/releases/download/v3.5.0/protobuf-all-3.5.0.zip \
    && unzip protobuf-all-3.5.0.zip \
    && cd protobuf-3.5.0 \
    && ./autogen.sh

RUN cd protobuf-3.5.0 \
    && ./configure \
    && make \
    && sudo make install

RUN cd protobuf-3.5.0/ \
    && sudo ldconfig

RUN rm -rf protobuf-3.5.0 protobuf-all-3.5.0.zip


# 6. Microsoft z3
ENV Z3_VERSION "4.5.0"
# install debian packages
RUN apt-get update -qq -y \
 && apt-get install binutils g++ make ant -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
#
# download, compile and install Z3
 && Z3_DIR="$(mktemp -d)" \
 && cd "$Z3_DIR" \
 && wget -qO- https://github.com/Z3Prover/z3/archive/z3-${Z3_VERSION}.tar.gz | tar xz --strip-components=1 \
 && python scripts/mk_make.py --java \
 && cd build \
 && make \
 && sudo make install \
 && cd / \
 && rm -rf "$Z3_DIR"

RUN sudo apt-get update
RUN sudo apt-get install -y glpk-utils libglpk-dev
RUN sudo pip install nose

RUN sudo apt-get install -y python-cffi
RUN sudo pip install six
RUN sudo apt-get install -y libssl-dev
RUN sudo mkdir app \
    && cd app \
    && curl -OL https://github.com/libgit2/libgit2/archive/v0.27.0.tar.gz \
    && ls \
    && tar xzf v0.27.0.tar.gz \
    && cd libgit2-0.27.0/ \
    && mkdir build && cd build \
    && cmake .. \
    && cmake --build . --target install \
    && sudo ldconfig \
    && rm -rf /app

RUN sudo apt-get install time

RUN sudo pip install sqlalchemy

################################################################################
# Set up user
#
# Run everything in the user space now
################################################################################
RUN mkdir /var/run/sshd
RUN chmod 0755 /var/run/sshd
RUN useradd -m biggroum
RUN groupadd admin
RUN usermod -a -G admin biggroum
RUN sudo chsh -s /bin/bash biggroum

# 7. Android SDK
# Set up environment variables
ENV ANDROID_HOME="/home/biggroum/android-sdk-linux" \
    SDK_URL="https://dl.google.com/android/repository/sdk-tools-linux-3859397.zip" \
    GRADLE_URL="https://services.gradle.org/distributions/gradle-4.5.1-all.zip"

USER biggroum
WORKDIR /home/biggroum

# Download Android SDK
RUN mkdir "$ANDROID_HOME" .android \
  && cd "$ANDROID_HOME" \
  && curl -o sdk.zip $SDK_URL \
  && unzip sdk.zip \
  && rm sdk.zip \
  && yes | $ANDROID_HOME/tools/bin/sdkmanager --licenses \
  && touch /home/biggroum/.android/repositories.cfg

# Install Gradle
RUN wget $GRADLE_URL -O gradle.zip \
  && unzip gradle.zip \
  && mv gradle-4.5.1 gradle \
  && rm gradle.zip \
  && mkdir .gradle

ENV PATH="/home/biggroum/gradle/bin:${ANDROID_HOME}/tools:${ANDROID_HOME}/platform-tools:${PATH}"

# Install platform tools
RUN cd android-sdk-linux/tools/bin \
    && ./sdkmanager "platform-tools" "platforms;android-10" "platforms;android-11" "platforms;android-12" "platforms;android-13" "platforms;android-14" "platforms;android-15" "platforms;android-16" "platforms;android-17" "platforms;android-18" "platforms;android-19" "platforms;android-20" "platforms;android-21" "platforms;android-22" "platforms;android-23" "platforms;android-24" "platforms;android-25" "platforms;android-26" "platforms;android-27" "platforms;android-7" "platforms;android-8" "platforms;android-9"
# Clone our repositories
RUN git clone https://github.com/cuplv/biggroum \
    && cd biggroum \
    && git submodule update --init --recursive \
    && git checkout develop

# Build the graph extractor
RUN cd biggroum/FixrGraphExtractor/ \
    && sbt oneJar \
    && cd ../

# Build the graph mining/frequent itemset mining tool
RUN cd biggroum/FixrGraphIso \
    && mkdir build \
    && cd build \
    && cmake ../ -DFIXR_GRAPH_EXTRACTOR_DIRECTORY=../../FixrGraphExtractor \
    && make \
    && cd ../../

# Build the protobuffer files
RUN protoc -I=./biggroum/FixrGraphExtractor/src/main/protobuf --python_out=./biggroum/python/fixrgraph/annotator/protobuf ./biggroum/FixrGraphExtractor/src/main/protobuf/proto_acdfg.proto \
    && protoc -I=./biggroum/FixrGraphExtractor/src/main/protobuf --python_out=./biggroum/python/fixrgraph/annotator/protobuf ./biggroum/FixrGraphExtractor/src/main/protobuf/proto_iso.proto

# Include the project in the PYTHONPATH variable
ENV PYTHONPATH=/home/biggroum/biggroum/python:$PYTHONPATH

USER biggroum
WORKDIR /home/biggroum

RUN cat /etc/passwd

# Run the tests
RUN cd biggroum/python/fixrgraph/test \
    && nosetests

# overwrite this with 'CMD []' in a dependent Dockerfile
CMD ["/bin/bash"]
