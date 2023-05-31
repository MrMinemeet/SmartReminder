import paho.mqtt.client as mqtt
import json
import time
import pyttsx3
import adafruit_rgb_display.ili9341 as ili9341
from PIL import Image, ImageDraw, ImageFont
import face_recognition
from picamera import PiCamera
import busio
import digitalio
from board import SCK, MOSI, MISO, D2, D3

MOSQUITTO_SERVER_IP = 'main.local'
MOSQUITTO_SERVER_PORT = 8883
DATA_FILE = 'data.json'
DOOR_TOPIC = 'door'
UPDATE_PERSON_TOPIC = 'update-person'
DETECTION_TIMEOUT_MS = 2000

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
        handle_door()
    elif msg.topic == UPDATE_PERSON_TOPIC:
        reload_tasks()

def handle_door():
    todos = try_detect_tasks_for_person()
    if todos is not None:
        display_todos(todos)
        say_todos(todos)
        clear_display()

def display_todos(todos):
    image = Image.new("RGB", (display.width, display.height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, display.width, display.height), outline=0, fill=(0, 0, 0))
    #TODO uhhh i dunno yet
    draw.text((0, 0), todos[0]['name'].join('\n'), fill="#FFFFFF")
    display.image(image)

def clear_display():
    image = Image.new("RGB", (display.width, display.height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, display.width, display.height), outline=0, fill=(0, 0, 0))
    display.image(image)

def say_todos(todos):
    #TODO due date
    for todo in todos:
        speaker.say(todo['name'])
        speaker.runAndWait()
        speaker.say(todo['decription'])
        speaker.runAndWait()
        speaker.say(f"Fällig am {todo['decription']}")
        speaker.runAndWait()

def try_detect_tasks_for_person():
    time = time.time()
    while time.time() - time < DETECTION_TIMEOUT_MS * 1000:
        snap = cam.read() #TODO optimize image (rescale, ...)
        encoding = face_recognition.face_encodings(snap)[0] #TODO no clue if this is working
        results = face_recognition.compare_faces(images, encoding)
        if len(results) > 0:
            first_match_index = results.index(True)
            return tasks[first_match_index]
    return None

def reload_tasks():
    data = json.load(DATA_FILE)
    tasks = []
    images = []

    people_groups = groupby(data, key=lambda x: x['personName'])
    index = -1
    for task, person in people_groups:
        if person not in people:
            index += 1
            images.append(face_recognition.load_image_file(person['image']))
            tasks.append([])
        tasks[index].append(task)

def main():
    speaker = pyttsx3.init()
    spi = busio.SPI(clock=SCK, MOSI=MOSI, MISO=MISO)
    display = ili9341.ILI9341(spi, cs=digitalio.DigitalInOut(D2), dc=digitalio.DigitalInOut(D3))
    print("Display Done")

    say_todos([{
        'name': 'Elias'
    }])
    display_todos([{
        'name': 'Elias'
    }])

    camera = PiCamera()
    camera.resolution = (1024, 768)
    print("Camera Done")

    reload_tasks()
    print("Loading Done")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MOSQUITTO_SERVER_IP, MOSQUITTO_SERVER_PORT, 60)
    print("MQTT Done")
    client.loop_forever()

if __name__ == "__main__":
    main()