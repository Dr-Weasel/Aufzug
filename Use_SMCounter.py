from SMCounter import SMCounter
from machine import Pin
import utime

counter = SMCounter(smID=0,InputPin=Pin(16,Pin.IN,Pin.PULL_UP))

while True:
    
    print(counter.value())
    utime.sleep(1)
