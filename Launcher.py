import subprocess
import time

# Start both scripts as background processes
# process1 = subprocess.Popen(['python', 'Dashboard.py'])
process1 = subprocess.Popen(['python', 'GUI.py'])
process2 = subprocess.Popen(['python', 'Sensor Simulator.py'])

try:
    while True:
        time.sleep(1) # Keep the master script alive
except KeyboardInterrupt:
    # Cleanly stop both if you press Ctrl+C
    process1.terminate()
    process2.terminate()
