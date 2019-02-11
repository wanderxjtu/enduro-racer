# enduro-racer
A django project for race management and result processing

## HOW TO START

- install develop environment

```
# install python >=3.6
# install pipenv
pipenv sync
```

- run in local env

```
pipenv shell
cd enduro-racer

# first time or after model change
python manager.py makemigrations 
python manager.py migrate

# first time
python manager.py createsuperuser

# start server
python manager.py runserver

```

