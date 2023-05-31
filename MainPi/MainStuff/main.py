import paho.mqtt.client as mqtt
import json
import time
import pyttsx3
from adafruit_rgb_display.st7789 import ST7789
from PIL import Image, ImageDraw, ImageFont
import face_recognition
from picamera import PiCamera
import busio
import digitalio
from board import SCK, MOSI, MISO, CE0, D24, D25

CS_PIN = CE0
DC_PIN = D25
RESET_PIN = D24
BAUDRATE = 24000000
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
    global display
    image = Image.new("RGB", (display.height, display.width))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, display.height, display.width),
                   outline=0, fill=(0, 0, 0))
    draw.text((0, 0), todos[0]['name'], fill="#FFFFFF")
    image = image.transpose(Image.FLIP_LEFT_RIGHT)
    display.image(image)

def clear_display():
    global display
    image = Image.new("RGB", (display.width, display.height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, display.width, display.height),
                   outline=0, fill=(0, 0, 0))
    display.image(image)

def say_todos(todos):
    global speaker
    # TODO due date
    for todo in todos:
        pass
        #speaker.say(todo['name'])
        #speaker.runAndWait()
        #speaker.say(todo['decription'])
        #speaker.runAndWait()
        #speaker.say(f"Fällig am {todo['decription']}")
        #speaker.runAndWait()

def try_detect_tasks_for_person():
    time = time.time()
    global tasks
    while time.time() - time < DETECTION_TIMEOUT_MS * 1000:
        snap = cam.read() # TODO optimize image (rescale, ...)
        encoding = face_recognition.face_encodings(
            snap)[0]  # TODO no clue if this is working
        results = face_recognition.compare_faces(images, encoding)
        if len(results) > 0:
            first_match_index = results.index(True)
            return tasks[first_match_index]
    return None

def reload_tasks():
    data = json.load(DATA_FILE)
    global tasks
    tasks = []
    global images
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
    global speaker
    # speaker = pyttsx3.init()
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
