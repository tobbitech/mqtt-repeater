#! /usr/bin/python3

import paho.mqtt.client as mqtt



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

while True:
    pass
    
