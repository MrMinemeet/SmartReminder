import base64
import io
import json
import os
import logging
from PIL import Image
import paho.mqtt.client as mqtt
import Task
import time

JSONPath: str = "datafile.json"
imagePath: str = "images"

indexes = dict()
index = 0
logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")


def on_connect(client, userdata, flags, rc):
    logger.info('Connected with result code %s', str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("addTask", qos=0)
    client.subscribe("addImage", qos=0)
    client.subscribe("getTask", qos=0)
    client.subscribe("getData", qos=0)
    client.subscribe("getAllPeople", qos=0)
    client.subscribe("removeTask", qos=0)


def on_message(client, userdata, msg):
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

def getTask(id: int):
    tasks = getJsonTasks()
    for t in tasks:
        if int(t["taskId"]) == id:
            client.publish("getTaskResponse", json.dumps(t))


def addTask(jsonStr: str):
    tasks = getJsonTasks()
    tasks.append(jsonStr)
    with open(JSONPath, "w") as file:
        json.dump(tasks, file)

    with open(JSONPath, "r") as file:
        text: str = file.read()

    text = text.replace("\\", "")
    text = text.replace("\\", "")
    text = text.replace("\"{\"", "{\"")
    text = text.replace("\"}\"", "\"}")

    with open(JSONPath, "w") as file:
        file.write(text)

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


def getJsonTasks() -> []:
    with open(JSONPath, "r") as file:
        if os.path.getsize(JSONPath) == 0:
            return []
        else:
            data = json.load(file)

            tasks = []
            for d in data:
                tasks.append(d)

            return tasks


def removeTask(id: int):
    tasks = getJsonTasks()
    for t in tasks:
        if int(t["taskId"]) == id:
            client.publish("removeTaskResponse", json.dumps(t))
            tasks.remove(t)

            with open(JSONPath, "w") as file:
                json.dump(tasks, file)

            with open(JSONPath, "r") as file:
                text: str = file.read()

            text = text.replace("\\", "")
            text = text.replace("\\", "")
            text = text.replace("\"{\"", "{\"")
            text = text.replace("\"}\"", "\"}")

            with open(JSONPath, "w") as file:
                file.write(text)


# save the image as jpeg somewhere and notify elias
def addImage(payload: str):
    data = json.loads(payload)
    imageData = data["image"]
    personName = data["personName"]

    convert_base64_to_jpg(imageData, personName)

    client.publish("ImageNotification", "personName")


def getData(payload: str):

    data = json.loads(payload)
    date = data["date"]
    name = data["personName"]

    data = getJsonTasks()
    for d in data:
        if d["dueDate"] == date and d["personId"] == name:
            client.publish("getDataResponse", json.dumps(d))


def getAllPeople() -> []:
    people = []
    with open(JSONPath, "r") as file:
        data = json.load(file)
        for d in data:
            people.append(d["personId"])

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
