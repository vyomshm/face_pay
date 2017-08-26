from flask import Flask, render_template, Response, flash, redirect
import cv2
import face_recognition

app = Flask(__name__)

my_image = face_recognition.load_image_file("suspects/Vyom.jpg")
my_face_encoding = face_recognition.face_encodings(my_image)[0]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []

vc = cv2.VideoCapture(0)

@app.route('/')
def home():
    """Video streaming home page."""
    return render_template('home.html')

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/verify')
def verify():
    if 'Vyom' in face_names:
        flash('face recognized')
        return render_template('liveness')

@app.route('/register/')
def register():
    return render_template('register.html')

def recognize_face(frame):
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        match = face_recognition.compare_faces([my_face_encoding], face_encoding)
        name = "Unknown"

        if match[0]:
            name = "Vyom"

        face_names.append(name)

    return face_locations, face_names

def get_output_frame(frame):
    face_locations, face_names= recognize_face(frame=frame)
    print('names:', face_names)
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    return frame, face_names


def gen():
    """Video streaming generator function."""
    while True:
        rval, frame = vc.read()
        frame, people = get_output_frame(frame)

        cv2.imwrite('t.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080, debug=False, threaded=True)