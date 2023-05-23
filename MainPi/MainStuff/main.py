import paho.mqtt.client as mqtt
import json
import face_recognition
from picamera import PiCamera
import time

MOSQUITTO_SERVER_IP = 'main.local'
MOSQUITTO_SERVER_PORT = 1883
DATA_FILE = 'data.json'
DOOR_TOPIC = 'door'
UPDATE_PERSON_TOPIC = 'update-person'
DETECTION_TIMEOUT_MS = 2000

people = []
images = []
camera = None

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
        #TODO print todo list on screen (person['name'], person['todos'])
        #TODO play todo list over speaker

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

    reload_people()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MOSQUITTO_SERVER_IP, MOSQUITTO_SERVER_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()