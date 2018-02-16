# Domoticz-Gatekeeper-Plugin
Domoticz Python plugin for eGardia, Woonveilig GATE01, GATE-02 and GATE03

After checking some modules to communicate with eGardia/Woonveilig I did find a semi standalone module for OpenHAB created by jeroenterheerdt/python-egardia here on Github. 

This module seemed to be the most promising to embedd into a Domoticz plugin. However despite my 25 years of programming experience I never developed in Python :). 

After trying to embed the class into a Domoticz Plugin for over a week I found out that the Domoticz Plugin system is not that flexible and a simple import of the python-egardia class into a plugin is not that easy. That’s why I decided to reuse the code of the python-egarida class in combination with the domoticz-woonveilig plugin created by StuffNL to create a complete new plugin that can talk to the GATE-01, GATE-02 and GATE-03 of eGardia / Woonveilig. 

The functions of the plugin:

-	Read the Gates devicelist and create the PIR and Switch devices
-	Create a extra device that contains the actual state of the Gate.

Todo:
-	Making the plugin more fail save
-	Let the plugin set the state of the Gate


Please note that the plugin is absolute without ANY warranty, and that this plugin is my first code written in Python. 

Installation:

cd domoticz/plugins
git clone https://github.com/System67/GateKeeper.git
