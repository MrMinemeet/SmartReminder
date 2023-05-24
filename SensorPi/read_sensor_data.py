import time
import datetime
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

# Callback-Function
def on_connect(client, userdata, flags, rc):
    print("Connected: " + str(rc))

def sensorCallback(channelHall, channelPressure):
  timestamp = time.time()
  stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

  if GPIO.input(channelPressure):
      start_zeitpunkt = time.time()
      while time.time() - start_zeitpunkt < 20:
          if(not GPIO.input(channelPressure)):
              # Open door
              print("Person opened the door " + stamp)

              broker = "mqtt.example.com"
              port = 1883

              client = mqtt.Client()

              # create connection
              client.on_connect = on_connect
              client.connect(broker, port, 60)

              # send message to broker
              client.publish("door", "Person opened the door")

              break
    time.sleep(5) # wait before checking for open door again

def main():
  try:
    # Loop until users quits with CTRL-C
    while True :
      time.sleep(0.1)
      sensorCallback(23,17)
  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

GPIO.setup(23 , GPIO.IN) # hall effect sensor
GPIO.setup(17,GPIO.IN) # pressure sensor

if __name__=="__main__":
   main()
