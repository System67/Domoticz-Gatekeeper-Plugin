# Domoticz Woonveilig / eGardia Gatekeeper
# Works with GATE-01, GATE-2 and GATE03
# Author: System67 (Carlo)
#
# Based on code from: 
#
# https://github.com/StuffNL/domoticz-woonveilig
# https://github.com/jeroenterheerdt/python-egardia
#
#
"""
<plugin key="GateKeeper" name="Woonveilig eGardia GateKeeper" version="1.0.0" author="System67 (Carlo)" wikilink="" externallink="">
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default=""/>
        <param field="Username" label="Username" width="150px" required="true" default=""/>
        <param field="Password" label="Password" width="150px" required="true" default=""/>
        <param field="Port" label="Port (default = 80)" width="150px" required="true" default=""/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug" default="true"/>
                <option label="False" value="Normal" />
            </options>
      </param>
        <param field="Mode1" label="Gate version" width="100px">
            <options>
                <option label="GATE-01" value="GATE-01"/>
                <option label="GATE-02" value="GATE-02"/>
                <option label="GATE-03" value="GATE-03"/>
            </options>  
      </param>
  </params>
  </plugin>
"""

import Domoticz
import http.client
import base64
import json

class BasePlugin:
    enabled = False
    _Credentials = ""
    _Sensors = {}
    _NrKey = "no"
    _TypeIR = ["IR","IR Sensor"]
    _TypesKeypad = ["Remote Keypad", "Keypad"]
    _SensorURL = ""
    _conn = None
    
    def __init__(self):
        #self.var = 123
        return

    def getItDone(self):
        Domoticz.Debug("GetItDone Called")

    def onStart(self):
        Domoticz.Debug("onStart called")
        
        # Set differences between gates in Constants
        if Parameters["Mode1"] == "GATE-01":
            self._SensorURL =  "/action/sensorListGet"
        else:
            self._SensorURL = "/action/deviceListGet"        
        
        if Parameters['Mode1'] == "GATE-03":
            self._TypeKey = "type_f"
            self._NrKey = "zone"
        
        self._Credentials = base64.b64encode("{0}:{1}".format(Parameters["Username"], Parameters["Password"]).encode()).decode("ascii")
        self._conn = http.client.HTTPConnection(Parameters["Address"],port=Parameters["Port"])
        
        self._conn.request("GET", self._SensorURL, headers={'Authorization': "Basic " + self._Credentials})
        r1 = self._conn.getresponse()
        
        results = r1.read().decode("utf-8", "ignore")
        Sensors = getSensors(Parameters['Mode1'],results)
        
        #Add new devices
        for Sensor in Sensors:
            SensorData = Sensors[Sensor]
            if (int(SensorData[self._NrKey]) not in Devices):
    
                if (SensorData['type'] == "Door Contact"): 
                    Domoticz.Device(Name=SensorData["name"], TypeName="Switch", Switchtype=11, Unit=int(SensorData[self._NrKey])).Create()
                if (SensorData['type'] in self._TypesKeypad and 99 not in Devices):
                    Options = {"LevelActions": "||","LevelNames": "Off|Home|On","LevelOffHidden": "false","SelectorStyle": "1"}
                    Domoticz.Device(Name=SensorData["name"], Unit=99, TypeName="Selector Switch", Switchtype=18, Image=13, Options=Options).Create()
                if (SensorData['type'] in self._TypeIR): 
                    Domoticz.Device(Name=SensorData["name"], TypeName="Switch", Switchtype=8, Unit=int(SensorData[self._NrKey])).Create()
    
        

    def onStop(self):
        Domoticz.Debug("onStop called")
        self._conn.close()

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        self._conn.request("GET", self._SensorURL, headers={'Authorization': "Basic " + self._Credentials})
        r1 = self._conn.getresponse()
        Domoticz.Debug(str(r1.status) +' : '+ r1.reason)
        results = r1.read().decode("utf-8", "ignore")
        Sensors = getSensors(Parameters['Mode1'],results)
        
        for Sensor in Sensors:
            SensorData = Sensors[Sensor]
            SensorState = getsensorstate(SensorData, Parameters["Mode1"] )
            if (SensorData["type"] == "Door Contact"): 
                UpdateDevice(int(SensorData[self._NrKey]), nValue = 1 if SensorState == False else 0, sValue = True if SensorState == False else True)
            if (SensorData["type"] in self._TypeIR): 
                UpdateDevice(int(SensorData[self._NrKey]), nValue = 1 if SensorState == True else 0, sValue = SensorState)        
    
        
        
        
        self._conn.request("GET", "/action/panelCondGet", headers={'Authorization': "Basic " + self._Credentials})
        r1 = self._conn.getresponse()
        Domoticz.Debug(str(r1.status) +' : '+ r1.reason)
        PanelData = r1.read().decode("utf-8", "ignore") 
        #PanelData = parseJson(results)
        
        Domoticz.Debug("CondGet result : "+str(PanelData))
        
        AlarmState = getstate(PanelData)
        Domoticz.Debug("Alarm State : "+AlarmState)
        
        if AlarmState == "DISARM":
            DomoState = 0
        elif AlarmState == "HOME":
            DomoState = 10
        elif AlarmState == "ARM":
            DomoState = 20

        UpdateDevice(Unit=99, nValue = DomoState, sValue= str(DomoState))

        
        
        
        

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return


def getSensors(prm_Version, prm_Data ):
    """Get the sensors and their states from the alarm panel"""
    
    sensord = parseJson(prm_Data)
    Domoticz.Debug(str(sensord))
    sensors = {}
    keyname = "no"
    typename = "type"
    # addjust keyname to Gate version
    if prm_Version in ["GATE-02", "GATE-03"]:
        keyname = "id"
    if prm_Version == "GATE-03":
        typename = "type_f"
        if prm_Version in ["GATE-02", "GATE-01"]:
            #Process GATE-01 and GATE-02 sensor json
            for sensor in sensord["senrows"]:
                #Change keyname from no to id to match GATE-02 and GATE-03
                if self._version == "GATE-01":
                    newkeyname = "id"
                    sensor[newkeyname] = sensor.pop(keyname)
                    sensors[sensor[newkeyname]] = sensor
                elif self._version == "GATE-02":
                    sensors[sensor[keyname]] = sensor
        elif prm_Version == "GATE-03":
            #Process GATE-03 sensor json
            for sensor in sensord["senrows"]:
                #Change type_f key to type for GATE-03.
                sensor["type"] = sensor.pop(typename)
                sensors[sensor[keyname]]=sensor
        return sensors

def getsensorstate(prm_Sensor, prm_Version):
    if prm_Sensor is not None:
        if prm_Version in ["GATE-01", "GATE-02"]:
            if len(prm_Sensor['cond']) > 0:
                # Return True when door is open or IR is triggered
                return True
            else:
                # Return False when door is closed or IR is not triggered
                return False
        elif prm_Version == "GATE-03":
            if prm_Sensor['status'].upper() == "DOOR OPEN" or len(prm_Sensor['status'])>0:
                # Return True when door is open or IR is triggered (todo)
                return True
            elif prm_Sensor['status'].upper() == "DOOR CLOSE" or len(prm_Sensor['status'])<=0:
                # Return False when door is closed or IR is not triggered (todo)
                return False
    else:
        return None


def parseJson(prm_jsonData):
    import json
    import re
    prm_jsonData = prm_jsonData.replace("/*-secure-","")
    prm_jsonData = prm_jsonData.replace("*/","")
    prm_jsonData = prm_jsonData.replace('{	senrows : [','{"senrows":[')
    property_names_to_fix = ["no","type","type_f","area", "zone", "name", "attr", "cond", "cond_ok", "battery", "battery_ok", "tamp", "tamper", "tamper_ok", "bypass", "rssi", "status", "id","su"]
    for p in property_names_to_fix:
        prm_jsonData = prm_jsonData.replace(p+' :','"'+p+'":')
    data = json.loads(prm_jsonData, strict=False)
    return data

def UpdateDevice(Unit, nValue, sValue):
# Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

def getstate(prm_PanelData):
    """Get the status from the alarm panel"""
    GATE03_STATES_MAPPING = {'FULL ARM':'ARM','HOME ARM 1':'HOME','HOME ARM 2':'HOME','HOME ARM 3':'HOME','DISARM':'DISARM'}

    if Parameters['Mode1'] in ["GATE-01", "GATE-02"]:
        ind1 = prm_PanelData.find('mode_a1 : "')
        numcharstoskip = 11
    elif Parameters['Mode1']  == "GATE-03":
        ind1 = prm_PanelData.find('"mode_a1" : "')
        numcharstoskip = 13
    prm_PanelData = prm_PanelData[ind1+numcharstoskip:]
    ind2 = prm_PanelData.find('"')
    status = prm_PanelData[:ind2]
    #Mapping GATE-03 states to supported values in HASS component
    if Parameters['Mode1']  == "GATE-03":
        status = GATE03_STATES_MAPPING.get(status.upper(), "UNKNOWN")
    return status.upper()
