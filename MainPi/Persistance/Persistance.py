import json
import typing

import Task
from typing_extensions import TypedDict

JSONPath: str = "datafile.json"
imagePath: str = ""

tasks = []
indexes = dict()


def addTask(name: str, personName: str, description: str, dueDate: str):
    task = Task.Task(name, description, personName, getFreeIndex(), dueDate)

    print(task)
    tasks.append(task)

    return


def removeTask(id: int) -> bool:
    with open(JSONPath, "r") as file:
        data = json.load(file)
        for d in data:
            if (d["id"] == id):
                print(d)
                return True

    return False

def addImage(personName: str, image):
    raise NotImplementedError


def getData(personName: str, date=None) -> str:
    with open(JSONPath, "r") as file:
        data = json.load(file)

        if date is None:
            print(data[0])  # this is a dict str:str
        else:
            for d in data:
                if (d["dueDate"] == date):
                    print(d)


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


def getAllPeople():
    raise NotImplementedError  # format to return?


if __name__ == '__main__':
    addTask("test", "this is a test", "Name1", "11.09.2001")
    addTask("test2", "this is a test too", "Name2", "11.09.2001")

    with open(JSONPath, "a+") as file:
        json.dump(tasks, file, default=Task.Task.to_json)

    getData("")
