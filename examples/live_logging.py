from kva import kva, LogFile
import time


kva.init(run_id="Logging Example")

kva.log(logfile=LogFile('logs.txt'))

for i in range(5):
    with open('logs.txt', 'a') as f:
        f.write(f"Log message {i}\n")
    time.sleep(1)

kva.finish()