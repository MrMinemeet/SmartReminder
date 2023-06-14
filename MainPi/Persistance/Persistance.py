import base64
import io
import json
import os
import logging
import time
from PIL import Image
import paho.mqtt.client as mqtt

JSONPath: str = "datafile.json"
imagePath: str = "images"

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")


def on_connect(mqttClient, userdata, flags, rc):
    logger.info('Connected with result code %s', str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqttClient.subscribe("addTask", qos=0)
    mqttClient.subscribe("addImage", qos=0)
    mqttClient.subscribe("getTask", qos=0)
    mqttClient.subscribe("getData", qos=0)
    mqttClient.subscribe("getAllPeople", qos=0)
    mqttClient.subscribe("removeTask", qos=0)


def on_message(mqttClient, userdata, msg):
    msg.payload = msg.payload.decode()
    if msg.topic == "addImage":
        print(msg.payload)
        addImage(msg.payload)
    elif msg.topic == "addTask":
        print(msg.payload)
        addTask(msg.payload)
    elif msg.topic == "getTask":
        print(msg.topic)
        getTask(int(msg.payload))
    elif msg.topic == "getData":
        print(msg.topic)
        getData(msg.payload)
    elif msg.topic == "getAllPeople":
        print(msg.topic)
        getAllPeople()
    elif msg.topic == "removeTask":
        removeTask(int(msg.payload))
    commandString = str(msg.payload)
    print(commandString)

    mqttClient.publish("update", "") # Just to notify the main programm that something new is here

def getTask(taskId: int):
    tasks = getJsonTasks()
    for t in tasks:
        if int(t["taskId"]) == taskId:
            client.publish("getTaskResponse", json.dumps(t))


def addTask(jsonStr: str):
    tasks = getJsonTasks()

    # Convert jsonString to dict object and add to list
    task = json.loads(jsonStr)
    task["taskId"] = len(tasks) + 1
    tasks.append(task)


    with open(JSONPath, "w", encoding='utf-8') as file:
        json.dump(tasks, file)

    client.publish("addTaskResponse", json.dumps(task))

#def addTask(name: str, personName: str, description: str, dueDate: str):
#    global index
#    task = Task.Task(name, description, personName, index, dueDate)
#    index = index + 1
#    tasks = getJsonTasks()
#
#    tasks.append(task)
#
#    with open(JSONPath, "w") as file:
#        json.dump(tasks, file, default=Task.Task.to_json)
#
#    return


def getJsonTasks() -> list[dict]:
    with open(JSONPath, "r", encoding='utf-8') as file:
        if os.path.getsize(JSONPath) == 0:
            return []
        else:
            data = json.load(file)
            return data


def removeTask(taskId: int):
    print("remove")
    tasks = getJsonTasks()
    for t in tasks:
        if int(t["taskId"]) == taskId:
            client.publish("removeTaskResponse", json.dumps(t))
            tasks.remove(t)

            with open(JSONPath, "w", encoding='utf-8') as file:
                json.dump(tasks, file)


# save the image as jpeg somewhere and notify elias
def addImage(payload: str):
    data = json.loads(payload)
    imageData = data["image"]
    personName = data["personName"]

    convert_base64_to_jpg(imageData, personName)


def getData(payload: str):

    data = json.loads(payload)
    date = data["date"]
    name = data["personName"]

    tasks = []

    data = getJsonTasks()
    for d in data:
        if d["dueDate"] == date and d["personName"] == name:
            tasks.append(d)
    

    client.publish("getDataResponse", json.dumps(tasks))


def getAllPeople() -> list[str]:
    people = []
    with open(JSONPath, "r", encoding='utf-8') as file:
        data = json.load(file)
        for d in data:
            people.append(d["personName"])

    # Make people unique
    people = list(dict.fromkeys(people))

    client.publish("getAllPeopleResponse", json.dumps(people))


def convert_base64_to_jpg(base64_string, personName):
    # Decode the Base64 string
    image_data = base64.b64decode(base64_string)

    # Create an in-memory stream
    image_stream = io.BytesIO(image_data)

    # Open the image using PIL
    image = Image.open(image_stream)

    # Save the image as PNG
    image.save(os.path.join(imagePath, personName)+".png", 'PNG')


if __name__ == '__main__':
    # setup mqtt
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("iot.soft.uni-linz.ac.at", 1883, keepalive=60)
    try:
        client.loop_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info('disconnecting ...')
        client.disconnect()
        time.sleep(1)
