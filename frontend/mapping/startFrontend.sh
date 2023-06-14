fuser -k 8080/tcp
fuser -k 3000/tcp
fuser -k 1100/tcp
fuser -k 7556/tcp
fuser -k 7555/tcp
sleep 1
python3 server.py & 
python3 server_mcm.py & 
mosquitto -p 1100 &
npm start
