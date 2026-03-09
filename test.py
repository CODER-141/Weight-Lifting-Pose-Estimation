import cv2
import mediapipe as mp
import numpy as np

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)

counter = 0
stage = None
target_reps = None
input_done = False
workout_done = False

entered_digits = ""

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        height, width, _ = image.shape

        # Prompt for target reps on screen
        if not input_done:
            cv2.rectangle(image, (0, 90), (480, 140), (50, 50, 50), -1)
            cv2.putText(image, "Enter number of squats using 0-9 then press Enter",
                        (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1, cv2.LINE_AA)
            if entered_digits:
                cv2.putText(image, f"Target Squats: {entered_digits}",
                            (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('Squat Workout', image)
            key = cv2.waitKey(1)

            if 48 <= key <= 57:
                entered_digits += chr(key)
            elif key == 13 or key == 10:
                if entered_digits:
                    target_reps = int(entered_digits)
                    input_done = True
            continue

        try:
            landmarks = results.pose_landmarks.landmark
            
            # Use left leg landmarks for squat tracking
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            angle = calculate_angle(hip, knee, ankle)

            # Display angle at knee position
            cv2.putText(image, str(round(angle, 2)),
                        tuple(np.multiply(knee, [width, height]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Check correctness of squat form
            # Good squat: knee angle should be between 70-160 degrees
            if 70 < angle < 160:
                feedback = "Good squat form!"
                color = (0, 255, 0)
            else:
                feedback = "Adjust your squat position"
                color = (0, 0, 255)

            cv2.putText(image, feedback, (20, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)

            # Squat counting logic (only if not done)
            if not workout_done:
                # Standing position (knee more extended)
                if angle > 140:
                    stage = "up"
                # Squat down position (knee more bent)
                if angle < 90 and stage == 'up':
                    stage = "down"
                    counter += 1

                if target_reps is not None and counter >= target_reps:
                    workout_done = True

        except:
            pass

        # Draw the UI box
        cv2.rectangle(image, (0, 0), (300, 80), (245, 117, 16), -1)

        # Squat count display
        cv2.putText(image, 'SQUATS', (15, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Stage display
        cv2.putText(image, 'STAGE', (90, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(stage), (90, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)



        # Workout done message
        if workout_done:
            cv2.putText(image, "Squat workout complete!", (120, 400),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)

        # Draw pose landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

        cv2.imshow('Squat Workout', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()