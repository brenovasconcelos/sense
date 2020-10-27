docker build -t sense .
docker run -d --name sense_flask -p 80:80 sense