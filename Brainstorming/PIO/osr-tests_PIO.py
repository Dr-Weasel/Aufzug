import time
from rp2 import PIO, StateMachine, asm_pio
from machine import Pin

# Define the blink program.  It has one GPIO to bind to on the set instruction, which is an output pin.
# Use lots of delays to make the blinking visible by eye.
@asm_pio(set_init=PIO.OUT_LOW)
def frequency():
    wrap_target()
    pull(noblock)
    mov(x, osr)
    jmp(not_osre, "skip1")
    set(pins, 1) [31]
    nop()        [31]
    nop()        [31]
    nop()        [31]
    nop()        [31]
    set(pins, 0) [31]
    jmp("idle")
    label("skip1")
    set(pins, 1) [31]
    nop()        [31]
    nop()        [31]
    nop()        [31]
    nop()        [31]
    set(pins, 0) [31]
    nop()        [31]
    nop()        [31]
    nop()        [31]
    nop()        [31]
    set(pins, 1) [31]
    nop()        [31]
    nop()        [31]
    nop()        [31]
    nop()        [31]
    set(pins, 0) [31]
    label("idle")
#     nop()        [31]
#     nop()        [31]
#     nop()        [31]
#     nop()        [31]
#     nop()        [31]
#     nop()        [31]
    jmp("idle")
    wrap()
    

# Instantiate a state machine with the blink program, at 2000Hz, with set bound to Pin(25) (LED on the rp2 board)
# sm = StateMachine(0, frequency, freq=2500, set_base=Pin(25))
led_blue = machine.Pin(12, 13, machine.Pin.OUT)

sm = StateMachine(0, frequency, freq=int(1e3), set_base=Pin(13))
# sm.put(1)
sm.active(1)
time.sleep(1)
# sm.put(1)


time.sleep(5)
sm.active(0)
sm.exec("set(pins,0)")
