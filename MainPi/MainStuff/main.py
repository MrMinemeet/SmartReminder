import paho.mqtt.client as mqtt
import json
import time
import pyttsx3
from adafruit_rgb_display.st7789 import ST7789
from PIL import Image, ImageDraw, ImageFont
import face_recognition
import numpy as np
from picamera import PiCamera
from itertools import groupby
import busio
import digitalio
from board import SCK, MOSI, MISO, CE0, D24, D25
from datetime import datetime
import cv2

CS_PIN = CE0
DC_PIN = D25
RESET_PIN = D24
BAUDRATE = 24000000
MOSQUITTO_SERVER_IP = 'main.local'
MOSQUITTO_SERVER_PORT = 1883
DATA_PATH = 'sample-data/'
DATA_FILE = 'data.json'
DOOR_TOPIC = 'door'
UPDATE_PERSON_TOPIC = 'update-person'
DETECTION_TIMEOUT_MS = 10000

tasks = []
images = []
camera = None
speaker = None
display = None

def on_connect(client, userdata, flags, rc):
    client.subscribe(DOOR_TOPIC)
    client.subscribe(UPDATE_PERSON_TOPIC)

def on_message(client, userdata, msg):
    if msg.topic == DOOR_TOPIC:
        print("Door opened message received")
        handle_door()
    elif msg.topic == UPDATE_PERSON_TOPIC:
        print("Tasks updated message received")
        reload_tasks()

def handle_door():
    todos = try_detect_tasks_for_person()
    if todos is not None:
        format_string = "%d.%m.%Y"
        today = datetime.today().date()
        todos = [todo for todo in todos if datetime.strptime(todo['dueDate'], format_string).date() == today]
        print("Showing todos")
        display_todos(todos)
        say_todos(todos)
        clear_display()
        print("Done showing todos")

def display_todos(todos):
    global display
    image = Image.new("RGB", (display.height, display.width))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, display.height, display.width),
                   outline=0, fill=(0, 0, 0))
    draw.text((0, 0), ''.join([todo['name'] + '\n' for todo in todos]), fill="#FFFFFF")
    image = image.transpose(Image.FLIP_LEFT_RIGHT)
    display.image(image)

def clear_display():
    global display
    image = Image.new("RGB", (display.height, display.width))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, display.height, display.width),
                   outline=0, fill=(0, 0, 0))
    display.image(image)

def say_todos(todos):
    global speaker
    if len(todos) == 0:
        speaker.say('Welcome home')
        speaker.runAndWait()
        return
    for todo in todos:
        speaker.say(todo['name'])
        speaker.runAndWait()
        speaker.say(todo['description'])
        speaker.runAndWait()

def try_detect_tasks_for_person():
    global camera
    global tasks
    ttime = time.time()
    while time.time() - ttime < DETECTION_TIMEOUT_MS / 1000: #retry for 10 seconds
        print("Looking for face")
        snap = np.empty((camera.resolution[1], camera.resolution[0], 3), dtype=np.uint8)
        camera.capture(snap, format='rgb') #take photo
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5) #resize for faster face detection
        face_locations = face_recognition.face_locations(frame) #find face locations
        print("Face locations:", face_locations)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        if len(face_encodings) > 0: #if we found at least 1 face
            face_encodings = face_encodings[0]
            #check if the first found face is a known user
            results = face_recognition.compare_faces(images, face_encodings)
            if len(results) > 0:
                #if we find a match, return this persons todos
                print("Face found")
                first_match_index = results.index(True)
                return tasks[first_match_index]
            else:
                print("No known face found")
                return None
    print("No face detected")
    return None

def reload_tasks():
    with open(DATA_PATH + DATA_FILE, 'r') as f:
        data = json.load(f)
        global tasks
        tasks = []
        global images
        images = []

        people_groups = groupby(data, key=lambda x: x['personName'])
        for person, person_tasks_group in people_groups:
            face_image = face_recognition.load_image_file(f'{DATA_PATH}{person}.png')
            face_encoding = face_recognition.face_encodings(face_image)[0]
            images.append(face_encoding)
            person_tasks = []
            for task in person_tasks_group:
                person_tasks.append(task)
            tasks.append(person_tasks)

def main():
    global speaker
    speaker = pyttsx3.init()
    print("Speaker loaded")

    spi = busio.SPI(clock=SCK, MOSI=MOSI, MISO=MISO)
    global display
    display = ST7789(
        spi,
        rotation=90,
        width=240,
        height=320,
        x_offset=0,
        y_offset=0,
        baudrate=BAUDRATE,
        cs=digitalio.DigitalInOut(CS_PIN),
        dc=digitalio.DigitalInOut(DC_PIN),
        rst=digitalio.DigitalInOut(RESET_PIN))
    print("Display loaded")

    global camera
    camera = PiCamera()
    camera.resolution = (1024, 768)
    print("Camera loaded")

    reload_tasks()
    print("Tasks loaded")

    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MOSQUITTO_SERVER_IP, MOSQUITTO_SERVER_PORT, 60)
    print("MQTT loaded")
    client.loop_forever()

if __name__ == "__main__":
    main()