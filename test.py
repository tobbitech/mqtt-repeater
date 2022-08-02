#! /usr/bin/python3

import mqttRepeater

adder = mqttRepeater.Adder( host="127.0.0.1", port=1883,  inTopic2="trollslottet/power_W", inTopic1="trollslottet/solarPower_W", subtract=True, outTopic="test")


while True:
    pass


