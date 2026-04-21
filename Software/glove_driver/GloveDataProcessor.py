import numpy as np
class GloveDataProcessor:
    def __init__(self):
        self.isCalibrationTime = True
        self.fingers = ["thumb", "index", "middle", "ring", "pinky"]
        self.calibration = {
            "thumb" : { "adc" : [], "pct" : [0,25,50,75,100]},
            "index" : { "adc" : [], "pct" : [0,25,50,75,100]},
            "middle" : { "adc" : [], "pct" : [0,25,50,75,100]},
            "ring" : { "adc" : [], "pct" : [0,25,50,75,100]},
            "pinky" : { "adc" : [], "pct" : [0,25,50,75,100]}

    }
    def adcToPercent(self, adcValue, finger):
        if self.isCalibrationTime == True:
            return
        cal = self.calibration[finger]
        result = np.interp(adcValue, cal["adc"], cal["pct"])
        return round(float(result), 1)

    def process(self, adcValues: tuple) -> dict:
        return {
            finger: self.adcToPercent(val, finger)
            for finger, val in zip(self.fingers, adcValues)
        }
    def addCalibrationPoint(self, finger, adcValue):
        if self.isCalibrationTime == False:
            return 
        if len(self.calibration[finger]["adc"]) < 5:
            self.calibration[finger]["adc"].append(adcValue)
        else:
            if self.checkCalibration() == True:
                self.isCalibrationTime = False
    def checkCalibration(self):
        for finger in self.calibration:
            if len(self.calibration[finger]["adc"]) < 5:
                return False
        return True
    def addCalibrationPointAllFingers(self,adcValues):
        if self.isCalibrationTime == False:
            return         
        for finger, val in zip(self.fingers, adcValues):
            self.addCalibrationPoint(finger,val)
        if self.checkCalibration() == True:
            self.isCalibrationTime = False
    def calibrateAgain(): 
        for f in self.calibration:
            self.calibration[f]["adc"] = []
        self.isCalibrationTime = True
   














    
