import face_recognition
import os
import cv2
import numpy as np


KNOWN_FACES_DIR = "my_face"
UNK_FACES_DIR = "unk_faces"
TOLERANCE = 0.5
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = "hog"

# video = cv2.VideoCapture(-1)
video = cv2.VideoCapture("1.mp4")

print("loading known faces...")

# Encode known faces if the program runs for the first time
# or Load the saved encodings
if(os.path.exists("known_faces.npy") and os.path.exists("known_names.npy")):
    print("exists")
    known_faces = np.load("known_faces.npy")
    known_names = np.load("known_names.npy")
else:
    known_faces = []
    known_names = []

    for name in os.listdir(KNOWN_FACES_DIR):
        for filename in os.listdir(f"{KNOWN_FACES_DIR}/{name}"):
            image = face_recognition.load_image_file(f"{KNOWN_FACES_DIR}/{name}/{filename}")
            encoding = face_recognition.face_encodings(image)[0]
            known_faces.append(encoding)
            known_names.append(name)

            known_faces = np.array(known_faces)
            known_names = np.array(known_names)
            np.save("known_faces.npy", known_faces)
            np.save("known_names.npy", known_names)



print("loading unknown faces...")

while True:
    ret, image = video.read()
    locations = face_recognition.face_locations(image, model=MODEL)
    encodings = face_recognition.face_encodings(image, locations)
    
    for face_encoding, face_location in zip(encodings, locations):
        results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
        match = None
        if True in results:
            match = known_names[results.index(True)]
            print(f"Match found: {match}")


            #draw rectangle arround face
            top_left = (face_location[3], face_location[0])
            bottom_right = (face_location[1], face_location[2])

            color = [0, 255, 0]
            print(type(top_left))
            print(top_left)
            cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

            top_left = (face_location[3], face_location[2])
            bottom_right = (face_location[1], face_location[2]+20)
            cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
            cv2.putText(
            image,
            match,
            (face_location[3]+10, face_location[2]+14),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200,200,200),
            FONT_THICKNESS)
            

    cv2.imshow("filename", image)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
