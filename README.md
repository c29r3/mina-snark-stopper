# mina-snark-stopper
Tool for Mina Protocol

## Description
This tool can be useful for Mina validators who run node at same time as block producer and snark worker. 
Worker can take up all processor time, which negatively affects block producer. When less than 3 minutes remain before the next proposal, the script disconnects the worker and starts it after 10 minutes.  

## Requirements
Python ver. 3.6+

## Install
*Your snark worker must be RUNNED*  
*Check the configuration file. There are some options you might want to reassign*
```
git clone https://github.com/c29r3/mina-snark-stopper.git \
&& cd mina-snark-stopper \
&& pip3 install -r requirements.txt \
&& python3 snark-stopper.py
```
