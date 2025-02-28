FROM ubuntu:22.04

# Install python3 and pip and other dependencies
RUN apt-get update && \
    apt-get install -y python3 \
        python3-pip \
        wget \
        libpq-dev

# User without privileges
SHELL ["/bin/bash", "--login", "-c"]

ENV USER=mlflow
ENV HOME=/home/${USER}

ENV UID 1000
ENV GID 100

RUN adduser --disabled-password \
    --gecos "Non-root user" \
    --home ${HOME} \
    --uid ${UID} \
    --gid ${GID} \
    ${USER}

# Set the entry point
COPY entrypoint.sh /
RUN chown ${UID}:${GID} /entrypoint.sh && \
    chmod 0755 /entrypoint.sh
    
# Activate the user
USER ${USER}

# Install miniconda
ENV CONDA_DIR=${HOME}/.conda
RUN ARCH=$(uname -i) && \
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-${ARCH}.sh -O ~/miniconda.sh && \
    chmod 0700 ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p ${CONDA_DIR} && \
    rm ~/miniconda.sh
ENV PATH=$CONDA_DIR/bin:$PATH

RUN echo "source ${CONDA_DIR}/etc/profile.d/conda.sh" >> ~/.profile
RUN conda init bash

# Work environment
RUN mkdir ${HOME}/{artifacts,mlruns}

ENV PROJECTS_DIR=${HOME}/mlflowProjects
RUN mkdir ${PROJECTS_DIR}
WORKDIR ${PROJECTS_DIR}

# Conda setup
ENV ENV_PREFIX=mlflow_env
RUN conda update --name base --channel defaults conda && \
    conda create -n $ENV_PREFIX && \
    conda clean --all --yes

RUN conda activate ${ENV_PREFIX} && \
    python3 -m pip install --upgrade pip && \
    pip install mlflow psycopg2-binary boto3
    # pip install hdfs

ENTRYPOINT ["/entrypoint.sh"]
EXPOSE 5000