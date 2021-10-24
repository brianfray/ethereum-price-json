## Terminal 1 
```sh
cd ethereum charts
python3 -m venv venv
. venv/bin/activate
export FLASK_ENV=development
export FLASK_APP=src
python3 -m pip install -r requirements.txt
flask run
```

## Terminal 2
```sh
cd ethereum charts
export FLASK_APP=src
export SECRET_KEY={CryptoCompare API KEY}
flask db
```

## Terminal 3
```sh
curl http://localhost:5000/api/price
```