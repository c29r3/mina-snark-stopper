# mina-snark-stopper
Tool for Mina Protocol

## Description
This tool can be useful for Mina validators who run node at same time as block producer and snark worker. 
Worker can take up all processor time, which negatively affects block producer. When less than `STOP_WORKER_BEFORE_MIN` minutes remain before the next proposal, the script disconnects the worker and starts it after `STOP_WORKER_FOR_MIN` minutes.  

## Requirements
Python ver. 3.6+

## Install
*Your snark worker must be RUNNED. Otherwise, the script will take the Block producer public key*  
*Check the configuration file. There are some options you might want to reassign*  
**If you run mina daemon through docker, then you need to add the flag `-p 127.0.0.1:3085:3085`**

### Tmux  
```
sudo apt-get update && sudo apt-get install tmux -y \
&& git clone https://github.com/c29r3/mina-snark-stopper.git \
&& cd mina-snark-stopper \
&& pip3 install -r requirements.txt \
&& tmux new -s snark-stopper -d python3 snark-stopper.py
```  
You can watch the snark-stopper work  
`tmux attach -t snark-stopper`  

Press to exit `ctrl + b` and then `d`

### Docker  
1. Download config file and change the parameters to suit you
```
wget https://raw.githubusercontent.com/c29r3/mina-snark-stopper/master/config.yml
```

2. Run docker container  
```
docker run -d \
--volume $(pwd)/config.yml:/mina/config.yml \
--net=host \
--restart always \
--name snark-stopper \
c29r3/snark-stopper
```

3. Check logs  
`docker logs -f snark-stopper`  
If you want to change some parameteres - change it in config file and then restart docker container  
`docker restart snark-stopper`  

#### Update docker image  
After running the command below, go to step 2
```
docker rm -f snark-stopper \
&& docker pull c29r3/snark-stopper
```

## Uninstall  
```
rm -rf mina-snark-stopper; \
docker rm -f snark-stopper; \
docker system prune -af
```
