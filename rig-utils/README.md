# Setup rigs for Gcloud upload and spike sorting

This guide explains how to set up a Windows workstation to:

1. Upload ephys data to cloud buckets
2. Run a spike sorting locally


## Install google cloud CLI (needed for cloud upload)

- Download and launch the the [google cloud CLI installer](https://cloud.google.com/sdk/docs/install#windows)

- Once done, open a terminal (or an anaconda prompt) and run:
    ```
    gcloud init

    gcloud auth login
    ```

- This will create a json file with the Gcloud credentials in:
    ```
    C:/Users/<your-user-name>/AppData/Roaming/gcloud/legacy_credentials/<google-user-email>/adc.json
    ```

- Create a new ENV variable called `GOOGLE_APPLICATION_CREDENTIALS` with the path to the json file as field.

## Install docker (needed for spike sorting)

- First, make sure virtualization is enabled (might require to change options in the BIOS), see [this guide](https://mashtips.com/enable-virtualization-windows-10/).

- Install WSL (Windows Subsystem for Linux) - [instructions](https://docs.microsoft.com/en-us/windows/wsl/install). When done, **Restart** and launch **Ubuntu** app to choose a username and password for the Linux subsystem.

- Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and follow the installation instructions. When done, logout and login again. Note that you need a [dockerhub](https://hub.docker.com/) account and to sign in to be able to pull images are run spike sorting in Docker.

## Make conda environment (needed for both)

- Install Anaconda or Miniconda

- Open the Anaconda Command Prompt and run the following:

```
conda create -n si python=3.9  # press y when prompted

# activate env
conda activate si

# install git 
conda install git

# clone and install spikeinterface (in develop mode)

git clone https://github.com/SpikeInterface/spikeinterface.git
cd spikeinterface
python setup.py develop
pip install -r requirements_full.txt
cd ..

# final additional steps to setup python docker-SDK
pip install docker
python C:/Users/<your-user-name>/Anaconda3/envs/si/Scripts/pywin32_postinstall.py -install

# package to speed up gcloud uploads
pip install -U crcmod
```

Make an environment variable called `SPIKEINTERFACE_DEV_PATH` that points to the cloned SpikeInterface repo (this is
temporary and needed to propagate the right SI version to the docker image -- won't be required after the next release).
