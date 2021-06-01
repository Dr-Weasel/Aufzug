import time
from rp2 import PIO, StateMachine, asm_pio
from machine import Pin

# Define the blink program.  It has one GPIO to bind to on the set instruction, which is an output pin.
# Use lots of delays to make the blinking visible by eye.
@asm_pio(set_init=PIO.OUT_LOW)
def frequency():
    pull()
    mov(y, osr)
    label("loop")
    set(pins, 1)
    mov(x, y)
    jmp("skip1")
    label("wait1")
    nop()               [3]
    label("skip1")
    nop()               [24]
    nop()               [19]
    jmp(x_dec, "wait1")
    set(pins, 0)
    mov(x, y)
    jmp("skip2")
    label("wait2")
    nop()               [2]
    label("skip2")
    nop()               [25]
    nop()               [19]
    jmp(x_dec, "wait2")
    jmp("loop")
    set(pins, 0)        # should be 100 cycles
    

# Instantiate a state machine with the blink program, at 2000Hz, with set bound to Pin(25) (LED on the rp2 board)
# sm = StateMachine(0, frequency, freq=2500, set_base=Pin(25))
led_blue = machine.Pin(12, machine.Pin.OUT)

sm = StateMachine(0, frequency, freq=int(1e8), set_base=Pin(12))

sm.active(1)
T = 1000     # Periodendauer in us
sm.put(T - 1)

led_state = led_blue.value()
# for i in range(1000):
#     if led_state != led_blue.value():
#         led_state = led_blue.value()
#         print(led_state)
#     time.sleep_ms(20)
sm.put(0)
time.sleep(10)
sm.active(0)
sm.exec("set(pins,0)")
