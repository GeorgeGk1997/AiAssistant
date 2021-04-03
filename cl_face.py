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


class Fac_rec:

    def __init__(self):
        
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
                    print(type(known_faces))
                    known_faces.append(encoding)
                    known_names.append(name)
                    print("Ok")

                    known_faces = np.array(known_faces)
                    known_names = np.array(known_names)
                    np.save("known_faces.npy", known_faces)
                    np.save("known_names.npy", known_names)

    def recogn_user(self, x):
        self.x = x

        known_faces = np.load("known_faces.npy")
        known_names = np.load("known_names.npy")
        video = cv2.VideoCapture(self.x)

        match_counter = 1
        previous_match = ""
        while True:
            ret, image = video.read()
            locations = face_recognition.face_locations(image, model=MODEL)
            encodings = face_recognition.face_encodings(image, locations)
            
            
            for face_encoding, face_location in zip(encodings, locations):
                results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
                match = None
                if True in results:
                    match = known_names[results.index(True)]

                    if previous_match == match:
                        match_counter += 1
                    elif match != "":
                        match_counter = 1



                    #draw rectangle arround face
                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])

                    color = [0, 255, 0]
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

                    if match_counter == 3:
                        print(f"Found: {match}")
                        cv2.destroyAllWindows()
                        return match

                    previous_match = match


            cv2.imshow("filename", image)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                return ""


# obj = Fac_rec()
# name = obj.recogn_user(-1)

# if name == "":
#     print("I cant recognise you. Try again!")
# else:
#     print(f"Welcome back {name}")


    