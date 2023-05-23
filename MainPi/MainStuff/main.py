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
MOSQUITTO_SERVER_PORT = 1883
DATA_FILE = 'data.json'
DOOR_TOPIC = 'door'
UPDATE_PERSON_TOPIC = 'update-person'
DETECTION_TIMEOUT_MS = 2000

people = []
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
        reload_people()

def handle_door():
    person = try_detect_person()
    if person is not None:
        display_todos(person)
        say_todos(person)
        clear_display()

def display_todos(person):
    image = Image.new("RGB", (display.width, display.height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, display.width, display.height), outline=0, fill=(0, 0, 0))
    draw.text((0, 0), person['todos'].join('\n'), fill="#FFFFFF")
    display.image(image)

def clear_display():
    image = Image.new("RGB", (display.width, display.height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, display.width, display.height), outline=0, fill=(0, 0, 0))
    display.image(image)

def say_todos(person):
    for todo in person['todos']:
        speaker.say(todo)
        speaker.runAndWait()

def try_detect_person():
    time = time.time()
    while time.time() - time < DETECTION_TIMEOUT_MS * 1000:
        snap = cam.read() #TODO optimize image (rescale, ...)
        encoding = face_recognition.face_encodings(snap)[0] #TODO no clue if this is working
        results = face_recognition.compare_faces(images, encoding)
        if len(results) > 0:
            first_match_index = results.index(True)
            return people[first_match_index]
    return None

def reload_people():
    data = json.load(DATA_FILE)
    people = []
    images = []
    for person in data:
        image = face_recognition.load_image_file(person['image'])
        encoding = face_recognition.face_encodings(image)[0]
        images.append(encoding)
        people.append({
            'name': person['name'],
            'todos': person['todos']
        })

def main():
    camera = PiCamera()
    camera.resolution = (1024, 768)

    speaker = pyttsx3.init()
    spi = busio.SPI(clock=SCK, MOSI=MOSI, MISO=MISO)
    display = ili9341.ILI9341(spi, cs=digitalio.DigitalInOut(D2), dc=digitalio.DigitalInOut(D3))

    reload_people()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MOSQUITTO_SERVER_IP, MOSQUITTO_SERVER_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()