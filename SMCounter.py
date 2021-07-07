from machine import Pin,Timer, PWM
from rp2 import PIO, asm_pio, StateMachine
    
@asm_pio()    
def PIO_COUNTER():
    set(x,0)
    wrap_target()
    label('loop')
    wait(0,pin,0)
    wait(1,pin,0)
    jmp(x_dec,'loop')
    wrap()
    
class SMCounter:
    
    def __init__(self, smID, InputPin):
        self.counter = 0x0
        self.sm = StateMachine(smID)
        self.pin = InputPin
        self.sm.init(PIO_COUNTER,freq=125_000_000,in_base=self.pin)
        self.sm.active(1)
    
    def value(self):
        self.sm.exec('mov(isr,x)')
        self.sm.exec('push()')
        self.counter = self.sm.get()
        return  (0x100000000 - self.counter) & 0xffffffff
    
    def reset(self):
        self.sm.active(0)
        self.sm.init(PIO_COUNTER,freq=125_000_000,in_base=self.pin)
        self.sm.active(1)
        

    def __del__(self):
        self.sm.active(0)