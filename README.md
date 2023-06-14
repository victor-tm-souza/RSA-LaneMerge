# RSA - Lane Merge

## Work contribution

* **50%** - Diogo Aguiar, 81020
* **50%** - Victor Souza, 89330

## Requirements

* Install xterm
```bash
sudo apt-get install xterm
```
* Install nodejs and make sure you have npm
* Install mosquitto broker
```bash
sudo apt install -y mosquitto
```
* Install the following python libraries (hope I didn't forget any)
```python
pip install websockets
pip install websocket
pip install paho-mqtt
```
* Install React dependencies. From inside ```./frontend/mapping/``` run:
```bash
npm install
```



## Instructions to run

1. In the [vanetza](https://code.nap.av.it.pt/mobility-networks/vanetza) folder, replace the docker-compose.yml by our docker-compose.yml in ```./vanetza-composer/```
2. Inside the vanetza folder, run: 
```bash 
docker compose up
```
3. Go to ```./frontend/mapping/``` and start the front-end, the socket servers and mosquitto broker by running:
```bash
./startFrontend.sh
```

4. Open Firefox and navigate to ```localhost:3000```. **Importan, use Firefox!** Google-chrome crashes mid run.
5. Go to ```./OBUs/``` and run
```
./runOBUs.sh
```
6. Enjoy the simulation running in the browser. (or simply watch ```./demonstration.webm```)

## If for some odd reason it doesn't work

1. Refresh firefox page
2. 
```bash
docker compose down
```
3. stop all OBUs (Which openned in xterm windows)
4. 
```bash
docker compose up
```
5. 
```bash
./runOBUs.sh
```


