from lcd_pico import I2cLcd
from machine import Pin, I2C
from _thread import start_new_thread, allocate_lock
import utime

lock = allocate_lock()


# init LEDs
led_green = Pin(13, Pin.OUT)
led_amber = Pin(14, Pin.OUT)
led_red = Pin(15, Pin.OUT)

# init display
display_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
LCD = I2cLcd(display_i2c, 39, 2, 16) # Address = 39, number of lines = 2, number of symbols per line = 16

# init hand encoder
encoder_clk = Pin(16, Pin.IN) # clock of hand encoder
encoder_dt = Pin(17, Pin.IN) # dt of hand encoder
encoder_sw = Pin(18, Pin.IN, Pin.PULL_UP) # switch of hand encoder

encoder_stepSpeed = [[200, 1], [175, 2], [150, 3], [137, 4], [125, 5], [120, 6], [115, 7], [110, 8], [105, 9],
             [100, 10], [95, 12], [90, 14], [85, 16], [80, 18], [75, 20], [50, 50], [25, 100], [20, 175],
             [15, 275], [10, 550]]

global encoder_counter
global encoder_acceleration

def hand_encoder_thread(clk, dt, stepSpeed):
    global encoder_counter
    global encoder_acceleration
    
    clk_lastState = [utime.ticks_ms(), utime.ticks_ms(), clk.value()] #2x time ticks required to avoid big count steps when a single click has a low delte time
    encoder_watchdog = 0

    while True:
        try:
            if encoder_watchdog >= 2500:
                led_green.toggle()
                encoder_watchdog = 0
            clk_value = clk.value()
            dt_value = dt.value()
                
            if clk_value != clk_lastState[2]:
                if clk_value == 1:
                    countStep = 1
                    currentTimeTicks = utime.ticks_ms()
                    if encoder_acceleration:
                        lastTimeTicks = clk_lastState[1]
                        if clk_lastState[0] > lastTimeTicks: lastTimeTicks = clk_lastState[0]
                        deltaTime = currentTimeTicks - lastTimeTicks
                        for speed in stepSpeed:
                            if deltaTime < speed[0]: countStep = speed[1]
                    if dt_value == 0:
                        lock.acquire()
                        encoder_counter += countStep
                        lock.release()
                    else:
                        lock.acquire()
                        encoder_counter -= countStep
                        lock.release()
                    clk_lastState[0] = clk_lastState[1]
                    clk_lastState[1] = currentTimeTicks
                
                clk_lastState[2] = clk_value
            utime.sleep_us(100)
            encoder_watchdog += 1
        except:
            print("Somthing went wrong, reading the encoder")

# start hand_encoder_thread
encoder_counter = 0
encoder_acceleration = True
start_new_thread(hand_encoder_thread, (encoder_clk, encoder_dt, encoder_stepSpeed))

# display
LCD.backlight_on()
lock.acquire()
counter = encoder_counter
lock.release()
counter_old = counter
LCD.clear()
LCD.putstr(str(counter))
print(counter)

while True:
    #try:
    led_red.toggle()
    lock.acquire()
    counter = encoder_counter
    lock.release()
    if counter != counter_old:
        text = str(counter)
        number_of_char = len(text)
        if number_of_char < 16:
            for i in range(16-number_of_char):
                text += " "
        #LCD.hal_write_command(0x02) #set cursor of display to home position
        #LCD.cursor_x = 0
        #LCD.cursor_y = 0
        LCD.move_to(0,0)
        LCD.putstr(text)
        print(counter)
        counter_old = counter
    utime.sleep_ms(250)
    #except:
        #print("Something went wrong, controlling the display")
