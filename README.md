<!-- PROJECT HEADING -->

<br />
<p align="center">
<h1 align="center">SeriesMaker-AIDE</h1>
<p align="center">
  <br />
  <a href="https://github.com/GSTT-CSC/SeriesMaker-AIDE">View repo</a>
  ·
  <a href="https://github.com/GSTT-CSC/SeriesMaker-AIDE/issues">Report Bug</a>
  ·
  <a href="https://github.com/GSTT-CSC/SeriesMaker-AIDE/issues">Request Feature</a>
  <br />
</p>


## Overview

SeriesMaker-AIDE is a simple AIDE app for testing DICOM end-to-end connectivity with clinical information
systems such as PACS or scanner software. The purpose of SeriesMaker-AIDE is to create a new dummy DICOM Series which
can be output to the originating DICOM Study. This is useful for testing new DICOM endpoints.

SeriesMaker-AIDE performs the following:

1. Ingests a DICOM Series
2. Duplicates the DICOM Series
3. Edits some basic DICOM metadata
   1. SeriesNumber
   2. InstanceNumber
4. Outputs the edited DICOM Series


## Developer Instructions

1. Download
```shell
git clone https://github.com/GSTT-CSC/SeriesMaker-AIDE.git
```

2. Setup virtual env
```shell
cd SeriesMaker-AIDE

python -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

3. Create `input` and `output` directories
```shell
mkdir input output
```

## Run source code with MONAI Deploy

1. Ensure Python venv running
2. Copy DICOM `.dcm` files to `input/` directory


```shell
monai-deploy exec app -i input/ -o -output/

# alternatively:
python app -i input/ -o output/
```

## Build and run as MONAI Application Package (MAP)

1. Ensure Python venv running
2. Ensure Docker running
3. Copy DICOM `.dcm` files to `input/` directory

```shell
# Package MAP
monai-deploy package app --tag ghcr.io/gstt-csc/seriesmaker-aide/map:0.1.0 -l DEBUG

# Test MAP with MONAI Deploy
monai-deploy run ghcr.io/gstt-csc/seriesmaker-aide/map:0.1.0 input/ output/

# Push MAP to GHCR
docker push ghcr.io/gstt-csc/seriesmaker-aide/map:0.1.0
```

### Optional 

Enter Docker container for testing

```shell
docker run --gpus all -it --rm -v /SeriesMaker-AIDE/input:/var/monai/input/ --entrypoint /bin/bash ghcr.io/gstt-csc/seriesmaker-aide/map:0.1.0
```

Run on specified GPU if machine has >1 available

```shell
CUDA_VISIBLE_DEVICES=2 monai-deploy run ghcr.io/gstt-csc/seriesmaker-aide/map:0.1.0 input/ output/
```