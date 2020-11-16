# mina-snark-stopper
Tool for Mina Protocol

## Description
This tool can be useful for Mina validators who run node at same time as block producer and snark worker. 
Worker can take up all processor time, which negatively affects block producer. When less than 3 minutes remain before the next proposal, the script disconnects the worker and starts it after 10 minutes.  

## Requirements
Python ver. 3.6+

## Install
*Your snark worker must be RUNNED. Otherwise, the script will take the Block producer public key*  
*Check the configuration file. There are some options you might want to reassign*

### Tmux  
```
sudo apt-get update && sudo apt-get install tmux -y \
&& git clone https://github.com/c29r3/mina-snark-stopper.git \
&& cd mina-snark-stopper \
&& pip3 install -r requirements.txt \
&& tmux new -s snark-stopper -d python3 snark-stopper.py
```

### Docker  
1. Install docker, clone repo, build image
```
sudo apt install docker.io -y \
&& git clone https://github.com/c29r3/mina-snark-stopper.git \
&& cd mina-snark-stopper \
&& docker build . -t snark-stopper
```

2. Run docker container  
```
docker run -d\
--net=host \
--restart always \
--name snark-stopper \
snark-stopper
```
