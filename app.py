from flask import Flask, render_template, redirect, url_for, request
import subprocess
import threading

app = Flask(__name__)

# Map exercise index (matching workout list order in index.html) to script filename
WORKOUT_SCRIPTS = {
    "0": "workout.py",          # Biceps Curl
    "1": "test.py",             # Squat
    "2": "overhead_press.py",   # Overhead Press
    "3": "deadlift.py",         # Deadlift
    "4": "barbell_row.py",      # Barbell Row
}

# Keep track of running processes per exercise
workout_processes = {}

def start_workout(exercise_id):
    global workout_processes
    script = WORKOUT_SCRIPTS.get(exercise_id)
    if script and exercise_id not in workout_processes:
        process = subprocess.Popen(["python", script])
        workout_processes[exercise_id] = process

def stop_workout(exercise_id):
    global workout_processes
    process = workout_processes.get(exercise_id)
    if process:
        process.terminate()
        del workout_processes[exercise_id]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start')
def start():
    exercise_id = request.args.get('id', '0')
    threading.Thread(target=start_workout, args=(exercise_id,)).start()
    return ('', 204)  # Return empty 204 so the page doesn't redirect

@app.route('/stop')
def stop():
    exercise_id = request.args.get('id', '0')
    stop_workout(exercise_id)
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)
