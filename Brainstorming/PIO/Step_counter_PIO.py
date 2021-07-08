import time
from rp2 import PIO, StateMachine, asm_pio
from machine import Pin

@asm_pio(set_init=PIO.OUT_LOW)
def frequency():
    """
    This function uses a PIO (state machine) for counting the number of driven steps.
    Use the put() function to send a new period time via the fifo to the state machine.
    The PIO will keep the frequency until a new period time is sent.
    One loop of the program uses 100 cycles.
    Run the program with a frequency of 100 kHz, so the period time, using put() will be in us.
    """
    pull(noblock)
    mov(x, osr) # x is only here for saving a valid value from pull; x will be recycled if pull(noblock) doesn't get a valid value from the fifo
    mov(y, osr)
    jmp(y_dec, "y_dec1")
    label("y_dec1")
    set(pins, 1)
    jmp("skip1")
    label("wait1")
    nop()               [4]
    label("skip1")
    nop()               [23]
    nop()               [19]
    jmp(y_dec, "wait1")
    set(pins, 0)
    mov(y, osr)
    jmp(y_dec, "y_dec2")
    label("y_dec2")
    jmp("skip2")
    label("wait2")
    nop()               [3]
    label("skip2")
    nop()               [24]
    nop()               [19]
    jmp(y_dec, "wait2")
    
sm = StateMachine(0, frequency, freq=int(1e8), set_base=Pin(12))

sm.put(1000) # Periodendauer in us  ## 1 kHz
sm.active(1)
time.sleep(2)
sm.put(500) # 2 kHz
time.sleep(2)
sm.put(250) # 4 kHz
time.sleep(2)
sm.put(125) # 8 kHz
time.sleep(2)
sm.put(1000000) # 1 Hz

time.sleep(5)
sm.active(0)
sm.exec("set(pins,0)")

