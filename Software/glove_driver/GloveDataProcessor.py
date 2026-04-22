import numpy as np
import logger as logger

class GloveDataProcessor:
    def __init__(self):

        self.logger = logger.Logger()

        self.isCalibrationTime = True
        self.fingers = ["thumb", "index", "middle", "ring", "pinky"]
        self.calibration = {
            "thumb" : { "adc" : [], "pct" : [0,25,50,75,100]},
            "index" : { "adc" : [], "pct" : [0,25,50,75,100]},
            "middle" : { "adc" : [], "pct" : [0,25,50,75,100]},
            "ring" : { "adc" : [], "pct" : [0,25,50,75,100]},
            "pinky" : { "adc" : [], "pct" : [0,25,50,75,100]}
        }
        
        self.logger.log("[GloveDataProcessor] initialized")

    def adcToPercent(self, adcValue, finger):
        if self.isCalibrationTime == True:
            return float(0.0)
        cal = self.calibration[finger]

        #sorting for interp to work correctly
        adc_points = np.array(cal["adc"])
        pct_points = np.array(cal["pct"])

        sorted_indices = np.argsort(adc_points)

        sorted_adc = adc_points[sorted_indices]
        sorted_pct = pct_points[sorted_indices]

        result = np.interp(adcValue, sorted_adc, sorted_pct)
        return round(float(result), 1)


    def process(self, adcValues: tuple) -> dict:
        #temporary fix for when we receive incomplete data packets
        result = {}

        if len(adcValues) != len(self.fingers):
            self.logger.log(f"[GloveDataProcessor] Received {len(adcValues)} ADC values, expected {len(self.fingers)}. Filling missing values with 0.")
        
        for i, finger in enumerate(self.fingers):
            if i < len(adcValues):
                result[finger] = self.adcToPercent(adcValues[i], finger)
            else:
                result[finger] = float(0.0)
        
        return result
        
        #if len(adcValues) != 5:
        #    return
        #return {
        #    finger: self.adcToPercent(val, finger)
        #    for finger, val in zip(self.fingers, adcValues)
        #}
    

    def addCalibrationPoint(self, finger, adcValue):
        if self.isCalibrationTime == False:
            return 
        
        if len(self.calibration[finger]["adc"]) < 5:
            self.calibration[finger]["adc"].append(adcValue)
        
        #fix bug of having to add 6 cal points
        if self.checkCalibration() == True:
            self.isCalibrationTime = False
            self.logger.log("[GloveDataProcessor] Calibration completed successfully.")


    def checkCalibration(self):
        for finger in self.calibration:
            if len(self.calibration[finger]["adc"]) < 5:
                return False
        return True
    

    def addCalibrationPointAllFingers(self, adcValues):
        
        if self.isCalibrationTime == False:
            self.logger.log("[GloveDataProcessor] Calibration already completed. Ignoring additional calibration points.")  
            return {"status": 1, "message": "Calibration already completed."}
        
        if len(adcValues) != len(self.fingers):
            self.logger.log(f"[GloveDataProcessor] Received {len(adcValues)} ADC values for calibration, expected {len(self.fingers)}. Ignoring this calibration attempt.") 
            return {"status": 2, "message": "Invalid number of ADC values. Expected 5."}
        
        for finger, val in zip(self.fingers, adcValues):
            self.addCalibrationPoint(finger, val)
        
        return {"status": 0, "message": "Calibration points added successfully."}
    
        #if self.isCalibrationTime == False:
        #    return         
        #for finger, val in zip(self.fingers, adcValues):
        #    self.addCalibrationPoint(finger,val)
        #if self.checkCalibration() == True:
        #    self.isCalibrationTime = False


    def calibrateAgain(self): 
        for f in self.calibration:
            self.calibration[f]["adc"] = []
        self.isCalibrationTime = True
        self.logger.log("[GloveDataProcessor] Calibration reset. Ready to calibrate again.")
   














    
