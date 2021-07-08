import time
from rp2 import PIO, StateMachine, asm_pio
from machine import Pin

@asm_pio(set_init=PIO.OUT_LOW)
def frequency():
    pull(noblock)
    mov(x, osr) # x is only here for saving a valid value from pull; x will be recycled if pull(noblock) doesn't get a valid value from the fifo
    mov(y, osr)
    set(pins, 1)
    jmp("skip1")
    label("wait1")
    nop()               [3]
    label("skip1")
    nop()               [24]
    nop()               [19]
    jmp(y_dec, "wait1")
    set(pins, 0)
    mov(y, osr)
    jmp("skip2")
    label("wait2")
    nop()               [2]
    label("skip2")
    nop()               [25]
    nop()               [19]
    jmp(y_dec, "wait2")
    
sm = StateMachine(0, frequency, freq=int(1e8), set_base=Pin(12))

T = 1000     # Periodendauer in us  ## 1 kHz
sm.put(T - 1)
sm.active(1)
time.sleep(1)
T = 500     # 2 kHz
sm.put(T - 1)
time.sleep(1)
T = 250     # 4 kHz
sm.put(T - 1)
time.sleep(1)
T = 125     # 8 kHz
sm.put(T - 1)
time.sleep(1)
T = 1000000     # 1 Hz
sm.put(T - 1)

time.sleep(5)
sm.active(0)
sm.exec("set(pins,0)")

