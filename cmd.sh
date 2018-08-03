docker run  --name pg -d -p 5432:5432 -e POSTGRES_PASSWORD=admin postgres:10.4 

apt update  

apt install -y python3-pip

apt install -y python3-tk

pip3 install pipenv==11.10.0

pipenv install --deploy

#pipenv run python Calculate.py

pipenv run python hello.py