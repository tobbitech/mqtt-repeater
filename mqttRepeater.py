#! /usr/bin/python3

import paho.mqtt.client as mqtt

def stringToValue(string):
    try:
        value = float(string)
        #print(value) 
    except:
        print("Message is not a numeric value: " + string)
        return('')
    else:
        return(value)

class Scaler:
    def __init__(self, host, port, inTopic, outTopic):
        self.host = host
        self.port = port
        self.inTopic = inTopic
        self.outTopic = outTopic
        self.scaleFactor = 1.0
        self.zeroValue = 0.0
        self.decimalPrecision = 1

        self.mqttClient = mqttClient = mqtt.Client("Scaler_for_" + inTopic)
        self.mqttClient.on_message=self.on_message 
        mqttClient.connect( host=self.host, port=self.port, keepalive=60)
        self.mqttClient.subscribe(self.inTopic)
        self.mqttClient.loop_start()

    def setScaleFactor(self, scaleFactor):
        self.scaleFactor = scaleFactor

    def setZeroValue(self, zeroValue):
        self.zeroValue = zeroValue

    def setDecimalPrecicion(self, decimalPrecision):
        self.decimalPrecision = decimalPrecision

    def on_message(self, client, userdata, message):
        message_text = str(message.payload.decode("utf-8"))
        #print("message received: " , message)
        value = 0.0
        scaledValue = 0.0

        # try to turn message into a number (float)
        try:
            value = float(message_text)
            #print(value) 
        except:
            print("Message is not a numeric value: " + message_text)
            print("message topic=",message.topic)
            print("message qos=",message.qos)
            print("message retain flag=",message.retain)
        else:
            scaledValue = value * self.scaleFactor + self.zeroValue
            # scaledValue_str = "{:." + str(self.decimalPrecision) + "f}".format(scaledValue)
            scaledValue_str = ("{:." + str(self.decimalPrecision) + "f}").format(scaledValue)
            print("Scaled value: " + scaledValue_str)
            self.mqttClient.publish(self.outTopic, scaledValue_str)
    

    def end(self):
        pass


class Adder:
    def __init__(self, host, port, inTopic1, inTopic2, outTopic, subtract = False):
        self.host = host
        self.port = port
        self.inTopic1 = inTopic1
        self.inTopic2 = inTopic2
        self.outTopic = outTopic
        self.subtract = subtract # if true, values in topics are added. If false, inTopic2 are subtracted from inTopic1
        self.decimalPrecision = 1

        self.inValue1 = None
        self.inValue2 = None

        # starting client to listen to MQTT inTopic1
        self.mqttClient1 = mqttClient1 = mqtt.Client("Adder_for_" + inTopic1)
        self.mqttClient1.on_message=self.on_message_inTopic1
        mqttClient1.connect( host=self.host, port=self.port, keepalive=60)
        self.mqttClient1.subscribe(self.inTopic1)
        self.mqttClient1.loop_start()

        self.mqttClient2 = mqttClient2 = mqtt.Client("Adder_for_" + inTopic2)
        self.mqttClient2.on_message=self.on_message_inTopic2
        mqttClient2.connect( host=self.host, port=self.port, keepalive=60)
        self.mqttClient2.subscribe(self.inTopic2)
        self.mqttClient2.loop_start()

    def setDecimalPrecicion(self, decimalPrecision):
        self.decimalPrecision = decimalPrecision

    def on_message_inTopic1(self, client, userdata, message):
        message_text = str(message.payload.decode("utf-8"))
        #print("message received: " , message)
        value = 0.0

        # try to turn message into a number (float)
        value = stringToValue(message_text)
        self.inValue1 = value

    def on_message_inTopic2(self, client, userdata, message):
        message_text = str(message.payload.decode("utf-8"))
        #print("message received: " , message)
        value = 0.0
        newValue = 0.0

        # try to turn message into a number (float)
        value = stringToValue(message_text)
        self.inValue2 = value

        # check if script has received values for both inValue1 and inValue2
        operation = "Added"
        if (not(self.inValue1 == None) and not (self.inValue2 == None) ):
            if ( self.subtract):
                newValue = self.inValue1 - self.inValue2
                operation = "subtracted"
            else:
                newValue = self.inValue1 + self.inValue2

            newValue_str = ("{:." + str(self.decimalPrecision) + "f}").format(newValue)
            print("inTopic1: (", self.inTopic1, "): ", self.inValue1, " inTopic2 (", self.inTopic2, "): " , self.inValue2, " -> ", operation, " value: " + newValue_str, sep='')

            self.mqttClient2.publish(self.outTopic, newValue_str)


if __name__ == "__main__":
   

    #mqtt.Client(client_id=””, clean_session=True, userdata=None, protocol=MQTTv311, transport=”tcp”)
    # mqttClient = mqtt.Client("repeater")
    # mqttClient.on_message=on_message 
    # mqttClient.connect( host="192.168.2.4", port=1883, keepalive=60)

    # topic = "trollslottet/terrace/waterLevel1"
    # mqttClient.subscribe(topic)

    # mqttClient.loop_start()

    # old tank
    waterTank1 = Scaler(host="192.168.2.4", port=1883, inTopic="trollslottet/terrace/waterLevel1", outTopic="trollslottet/terrace/waterLevel1_L")
    #waterTank1.setScaleFactor(1000.0/9000.0)
    waterTank1.setScaleFactor(0.1759843371) # copiend from watertank 2
    waterTank1.setZeroValue(-600) # guessed based on one measurement
    waterTank1.setDecimalPrecicion(0)


    # new tank (butylacetate)
    waterTank2 = Scaler(host="192.168.2.4", port=1883, inTopic="trollslottet/terrace/waterLevel2", outTopic="trollslottet/terrace/waterLevel2_L")
    waterTank2.setScaleFactor(0.1759843371) # calculated in google sheet
    waterTank2.setZeroValue(-718) # calculated in google sheet
    waterTank2.setDecimalPrecicion(0)

    # Calculate power consumption
    powerConsumtion = Adder( host="192.168.2.4", port=1883,  inTopic2="trollslottet/power_W", inTopic1="trollslottet/solarPower_W", subtract=True, outTopic="trollslottet/powerConsumptionCalc")

    while True:
        pass
    
