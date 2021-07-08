import utime
from rp2 import PIO, StateMachine, asm_pio
from machine import Pin

@asm_pio(set_init=PIO.OUT_LOW)
def PIO_FREQUENCY():
    """
    This function uses a PIO (state machine) for generating a reliable frequency.
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
    
class SMFrequency:
    def __init__(self, smID, OutputPin):
        self.sm = StateMachine(smID)
        self.pin = OutputPin
        self.sm.init(PIO_FREQUENCY, freq = 100_000_000, set_base = self.pin)
    
    def set_period_us(self, period_us):
        self.sm.put(period_us)
    
    def active(self, active):
        self.sm.active(active)
        if active == 0:
            self.sm.exec("set(pins,0)")
        
    def __del__(self):
        self.sm.active(0)
        self.sm.exec("set(pins,0)")
        
if __name__ == "__main__":
    freq = SMFrequency(smID = 1, OutputPin = Pin(2, Pin.OUT))
    freq.set_period_us(500)
    freq.active(1)
    utime.sleep(2)
    freq.active(0)
    