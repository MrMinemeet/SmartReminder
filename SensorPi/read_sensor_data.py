import time
import datetime
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

# Callback-Function
def on_connect(client, userdata, flags, rc):
    print("Connected: " + str(rc))

def sensorCallback(client,channelHall, channelPressure):
  timestamp = time.time()
  stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

  if GPIO.input(channelPressure):
      start_zeitpunkt = time.time()
      while time.time() - start_zeitpunkt < 20:
          if(not GPIO.input(channelHall)):
              # Open door
              print("Person opened the door " + stamp)

              # send message to broker
              client.publish("door", "Person opened the door")

              time.sleep(5) # wait before checking for open door again
              break

def main():
  try:
    broker = "main.local"
    port = 1883

    # create connection
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(broker, port, 60)

    # Loop until users quits with CTRL-C
    while True :
      time.sleep(0.1)
      sensorCallback(client,23,17)
  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()
  except Exception as e:
    print(str(e))
    GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

GPIO.setup(23 , GPIO.IN) # hall effect sensor
GPIO.setup(17,GPIO.IN) # pressure sensor

if __name__=="__main__":
   main()
