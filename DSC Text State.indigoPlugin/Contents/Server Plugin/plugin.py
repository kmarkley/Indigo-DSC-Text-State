#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# http://www.indigodomo.com

import indigo

# Note the "indigo" module is automatically imported and made available inside
# our global name space by the host process.

###############################################################################
# globals

################################################################################
class Plugin(indigo.PluginBase):
    ########################################
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
    
    def __del__(self):
        indigo.PluginBase.__del__(self)

    ########################################
    # Start, Stop and Config changes
    ########################################
    def startup(self):
        self.debug = self.pluginPrefs.get("showDebugInfo",False)
        self.logger.debug("startup")
        if self.debug:
            self.logger.debug("Debug logging enabled")
        self.deviceDict = dict()
        indigo.devices.subscribeToChanges()

    ########################################
    def shutdown(self):
        self.logger.debug("shutdown")
        self.pluginPrefs["showDebugInfo"] = self.debug

    ########################################
    def closedPrefsConfigUi(self, valuesDict, userCancelled):
        self.logger.debug("closedPrefsConfigUi")
        if not userCancelled:
            self.debug = valuesDict.get("showDebugInfo",False)
            if self.debug:
                self.logger.debug("Debug logging enabled")

    ########################################
    def validatePrefsConfigUi(self, valuesDict):
        self.logger.debug("validatePrefsConfigUi")
        errorsDict = indigo.Dict()
                
        if len(errorsDict) > 0:
            return (False, valuesDict, errorsDict)
        return (True, valuesDict)
    
    ########################################
    # Device Methods
    ########################################
    def deviceStartComm(self, dev):
        self.logger.debug("deviceStartComm: "+dev.name)
        if dev.version != self.pluginVersion:
            self.updateDeviceVersion(dev)
        if dev.id not in self.deviceDict:
            theProps = dev.pluginProps
            self.deviceDict[dev.id] = {'dev':dev, 'keypad':indigo.devices[int(theProps['keypad'])]}
            self.updateDeviceStatus(dev)
    
    ########################################
    def deviceStopComm(self, dev):
        self.logger.debug("deviceStopComm: "+dev.name)
        if dev.id in self.deviceDict:
            del self.deviceDict[dev.id]
    
    ########################################
    def validateDeviceConfigUi(self, valuesDict, typeId, devId, runtime=False):
        self.logger.debug("validateDeviceConfigUi: " + typeId)
        errorsDict = indigo.Dict()
        
        if len(errorsDict) > 0:
            return (False, valuesDict, errorsDict)
        return (True, valuesDict)
    
    ########################################
    def updateDeviceVersion(self, dev):
        theProps = dev.pluginProps
        # update states
        dev.stateListOrDisplayStateIdChanged()
        # check for props
        
        # push to server
        theProps["version"] = self.pluginVersion
        dev.replacePluginPropsOnServer(theProps)
    
    ########################################
    def updateDeviceStatus(self, dev):
        self.logger.debug("updateDeviceStatus: " + dev.name)
        theProps = dev.pluginProps
        keypad = self.deviceDict[dev.id]['keypad']
        newStates = []
        
        if keypad.states['state.disarmed']:
            onState      = False
            shortState   = ["Not Ready","Ready"][keypad.states['ReadyState.ready']]
            displayState = "Disarmed (%s)" % shortState
        elif keypad.states['state.armed']:
            onState      = True
            shortState   = keypad.states['ArmedState']
            displayState = "%s %s" % (shortState, keypad.states["state"])
        elif keypad.states['state.exitDelay']:
            onState      = False
            shortState   = "Exit"
            displayState = "Exit Delay"
        elif keypad.states['state.entryDelay']:
            onState      = True
            shortState   = "Entry"
            displayState = "Entry Delay"
        elif not keypad.states['PanicState.none']:
            onState      = True
            shortState   = "Panic"
            displayState = "Panic"
            if not keypad.states['PanicState.panic']:
                displayState = displayState + " (%s)" % keypad.states['PanicState']
        elif keypad.states['state.tripped']:
            onState      = True
            shortState   = "Tripped"
            displayState = "Tripped"
        else:   # shouldn't be anything left, but just in case
            onState      = False
            shortState   = keypad.states['state']
            displayState = keypad.states['state']
        
        newStates.append({'key':'onOffState','value':onState})
        newStates.append({'key':'shortState','value':shortState.title()})
        newStates.append({'key':'state','value':displayState.title()})
        
        # update device
        dev.updateStatesOnServer(newStates)
    
    ########################################
    # Device updated
    ########################################
    def deviceUpdated(self, oldDev, newDev):

        if (oldDev.pluginId == self.pluginId) or (newDev.pluginId == self.pluginId):
            indigo.PluginBase.deviceUpdated(self, oldDev, newDev)
        
        elif newDev.pluginId == "com.frightideas.indigoplugin.dscAlarm" and newDev.deviceTypeId == "alarmKeypad":
            for devId in self.deviceDict:
                keypad = self.deviceDict[devId]['keypad']
                if newDev.id == keypad.id:
                    self.logger.debug("deviceUpdated: "+newDev.name)
                    # keep a copy of the updated device
                    self.deviceDict[devId]['keypad'] = newDev
                    # update the device
                    self.updateDeviceStatus(self.deviceDict[devId]['dev'])
    
    ########################################
    # Menu Methods
    ########################################
    def toggleDebug(self):
        if self.debug:
            self.logger.debug("Debug logging disabled")
            self.debug = False
        else:
            self.debug = True
            self.logger.debug("Debug logging enabled")
    
    ########################################
    # Menu Callbacks
    ########################################
    def getKeypadDeviceList(self, filter="", valuesDict=None, typeId="", targetId=0):
        devList = []
        for dev in indigo.devices.iter(filter='com.frightideas.indigoplugin.dscAlarm'):
            if dev.deviceTypeId == "alarmKeypad":
                devList.append((dev.id, dev.name))
        return devList        
