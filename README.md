# A proposal for ENGIE's powerplant-coding-challenge

A proposal to the challenge offered by the SPaaS team of ENGIE/GEM: a REST API exposing a POST method that takes a payload as you can find in the `resource/example_payloads` directory
and that returns a json with the same structure as in `resource/example_response.json`.

The REST API has been developed in Python using Flask framework, and a Dockerfile has been added for the extra
challenge. Power is allocated using a queuing system in order to have a cost efficient repartition of power across the
available powerplants.

A few notes concerning the challenge:

- different powerplants may have the same name (cf. `example_response.json`)
- the *ALLOW_FLOAT* flag in `api/settings.py` can be set to *False* if you prefer to have integer values in your
responses (assuming that the pmin and pmax values in the payload are whole numbers)
- if run with your local interpreter, the log outputs will be sent to stderr, and if run with Docker the logs will be
saved at `/var/log/uwsgi` in the container.

For more information about the challenge please refer to the challenge resource.

## Requirements

- Docker
- or Python3 if run with the local interpreter

P.S. The following content has been written for an Unix environment.

## Installation

### Via Docker

Build the Docker image from the Dockerfile by running:

```bash
docker build -t powerplant-coding-challenge .
```

Run the container:

```bash
docker run -d -p 5000:5000 powerplant-coding-challenge
```

If you would like to access the app's logs locally, the following command will run the container and create a directory
called `log` in your current directory and bindmount it to `/var/log/uwsgi`in the container.

```bash
docker run -d -p 5000:5000 -v ${PWD}/log:/var/log/uwsgi powerplant-coding-challenge
```

### Via the local interpreter

Assuming that you are in a Python3 virtual environment, install the required dependencies with the following command:

```bash
pip install -r requirements.txt
```
Run the app:

```bash
python run.py
```

Or via the following command:

```bash
FLASK_APP=run.py FLASK_ENV=development flask run
```

## Usage

Once the installation complete, the API should be exposed at <http://localhost:5000/> and <http://localhost:5000/api/v0/>.

You may run the following cURL command to make a HTTP POST request with one of the payload examples provided:

```bash
curl -X POST http://127.0.0.1:5000/api/v0\
    --data "@resource/example_payloads/payload1.json"\
    --header "Content-Type: application/json"
```

You should receive a JSON format response with the allocated power for the given payload.

For more information about the required payload please refer to the challenge resource.

## Author

Shoei Kadogami, consultant at Intys Data  
telephone: +32 487 59 42 58  
email: shoei.kadogami@intys.eu
