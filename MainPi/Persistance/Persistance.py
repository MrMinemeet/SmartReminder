import json
import typing
import os
import Task
from typing_extensions import TypedDict
import io
import base64
from PIL import Image

JSONPath: str = "datafile.json"
imagePath: str = "images"

indexes = dict()


def addTask(name: str, personName: str, description: str, dueDate: str):
    task = Task.Task(name, description, personName, getFreeIndex(), dueDate)
    tasks = getJsonTasks()

    tasks.append(task)

    with open(JSONPath, "w") as file:
        json.dump(tasks, file, default=Task.Task.to_json)

    return


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


def removeTask(id: int) -> bool:
    tasks = getJsonTasks()
    for t in tasks:
        if t["id"] == id:
            tasks.remove(t)
            return True

    return False


# save the image as jpeg somewhere and notify elias
def addImage(personName: str, imageData):
    convert_base64_to_jpg(imageData, personName)


def getData(personName: str, date=None) -> str:
    with open(JSONPath, "r") as file:
        data = json.load(file)

        if date is None:
            print(data[0])  # this is a dict str:str
        else:
            for d in data:
                if d["dueDate"] == date:
                    print(d)
    return ""


def getFreeIndex():
    index = None

    for key in indexes.keys():
        if not indexes[key]:
            index = key
            break

    if index is None:
        index = len(indexes.keys())

    indexes[index] = True

    return index


def getAllPeople() -> []:
    people = []
    with open(JSONPath, "r") as file:
        data = json.load(file)
        for d in data:
            people.append(d["personName"])

    return people


def convert_base64_to_jpg(base64_string, personName):
    # Decode the Base64 string
    image_data = base64.b64decode(base64_string)

    # Create an in-memory stream
    image_stream = io.BytesIO(image_data)

    # Open the image using PIL
    image = Image.open(image_stream)

    # Save the image as JPEG
    image.save(imagePath + personName, 'PNG')