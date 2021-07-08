import machine
import utime

led_red = machine.Pin(15, machine.Pin.OUT)
led_amber = machine.Pin(14, machine.Pin.OUT)
led_green = machine.Pin(13, machine.Pin.OUT)
blue = machine.Pin(12, machine.Pin.OUT)

led_red.value(0)
led_amber.value(0)
led_green.value(0)

encoderCLK = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_DOWN)
encoderDT = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_DOWN)
encoderSW = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)

acceleration = True

#stepSpeed defines, how many steps are done per klick (second value in the lists). This depends on how many milliseconds elapse between tow clicks (first value in the lists).
stepSpeed = [[200, 1], [175, 2], [150, 3], [137, 4], [125, 5], [120, 6], [115, 7], [110, 8], [105, 9],
             [100, 10], [95, 12], [90, 14], [85, 16], [80, 18], [75, 20], [50, 50], [25, 100], [20, 175],
             [15, 275], [10, 550]]

encoderCounter = 0
clkLastState = [utime.ticks_ms(), utime.ticks_ms(), encoderCLK.value()] #2x time ticks required to avoid big count steps when a single click has a low delte time

print(encoderCounter)

while True:
    #try:
    led_red.value(encoderCLK.value())
    led_green.value(encoderDT.value())
    led_amber.value(encoderSW.value())
    
    clkState = encoderCLK.value()
    dtState = encoderDT.value()
        
    if clkState != clkLastState[2]:
        if clkState == 1:
            countStep = 1
            currentTimeTicks = utime.ticks_ms()
            if acceleration:
                lastTimeTicks = clkLastState[1]
                if clkLastState[0] > lastTimeTicks: lastTimeTicks = clkLastState[0]
                deltaTime = currentTimeTicks - lastTimeTicks
                for speed in stepSpeed:
                    if deltaTime < speed[0]: countStep = speed[1]
            if dtState == 0:
                encoderCounter += countStep
            else:
                encoderCounter -= countStep
            print(encoderCounter)
            clkLastState[0] = clkLastState[1]
            clkLastState[1] = currentTimeTicks
        
        clkLastState[2] = clkState
    utime.sleep_us(100)
    #except:
        #pass