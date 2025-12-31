import subprocess
import time

# Start both scripts as background processes
process1 = subprocess.Popen(['python', 'src/gui.py'])
process2 = subprocess.Popen(['python', 'src/simulator.py'])

try:
    while True:
        time.sleep(1) # Keep the master script alive
except KeyboardInterrupt:
    # Cleanly stop both if you press Ctrl+C
    process1.terminate()
    process2.terminate()
