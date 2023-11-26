FROM python:3.8-slim-buster

#set wrk dir
WORKDIR /app

#copy into container
COPY . /app

#upgrade pip
RUN pip install --upgrade pip

#install needed packages
RUN pip install --no-cache-dir -r requirements.txt

#set default commands to run when starting container
CMD ["python", "app.py"]