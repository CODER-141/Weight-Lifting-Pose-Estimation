from flask import Flask, render_template, redirect, url_for
import subprocess
import threading
import os
import signal

app = Flask(__name__)
workout_process = None

def start_workout():
    global workout_process
    if workout_process is None:
        workout_process = subprocess.Popen(["python", "workout.py"])

def stop_workout():
    global workout_process
    if workout_process:
        workout_process.terminate()
        workout_process = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start')
def start():
    threading.Thread(target=start_workout).start()
    return redirect(url_for('home'))

@app.route('/stop')
def stop():
    stop_workout()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
