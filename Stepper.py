"""Micropython module for stepper motor driven by Easy Driver."""
from machine import Pin, PWM
from utime import sleep_us, sleep_ms, ticks_us, ticks_ms



class Stepper:
    """Class for stepper motor driven by Easy Driver."""

    def __init__(self, step_pin, dir_pin, sleep_pin, pwm_pin):
        """Initialise stepper."""
        self.stp = step_pin
        self.dir = dir_pin
        self.slp = sleep_pin
        self.pwm = PWM(pwm_pin)

        self.stp.init(Pin.OUT)
        self.dir.init(Pin.OUT)
        self.slp.init(Pin.OUT)

        self.step_time = 1000  # us
        self.steps_per_rev = 1600
        self.current_position = 0

    def power_on(self):
        """Power on stepper."""
        self.slp.value(1)

    def power_off(self):
        """Power off stepper."""
        self.slp.value(0)
        self.current_position = 0

    def steps(self, step_count):
        """Rotate stepper for given steps."""
        self.dir.value(0 if step_count > 0 else 1)
        steps_ramp = self.ramp(500, self.step_time, 1000)
        steps = abs(step_count) - steps_ramp
        for i in range(steps): # TODO: Rampe darf nicht mehr Schritte brauchen als gefahren werden sollen
            self.stp.value(1)
            sleep_us(self.step_time)
            self.stp.value(0)
            sleep_us(self.step_time)
        self.current_position += step_count

    def rel_angle(self, angle):
        """Rotate stepper for given relative angle."""
        steps = int(angle / 360 * self.steps_per_rev)
        self.steps(steps)

    def abs_angle(self, angle):
        """Rotate stepper for given absolute angle since last power on."""
        steps = int(angle / 360 * self.steps_per_rev)
        steps -= self.current_position % self.steps_per_rev
        self.steps(steps)

    def revolution(self, rev_count):
        """Perform given number of full revolutions."""
        self.steps(rev_count * self.steps_per_rev)

    def set_step_time(self, us):
        """Set time in microseconds between each step."""
        if us < 20:  # 20 us is the shortest possible for esp8266
            self.step_time = 20
        else:
            self.step_time = us
            
    def ramp(self, step_time_start, step_time_end, ramp_time):
        """Applies a ramp from step_time_start (in us) to step_time_end (in us) within the ramp_time (in ms)."""
        now = ticks_us()
        t_start = now
        t_ramp = ramp_time * 1000 # ramp_time is in ms, all other times in us
        m = (step_time_end - step_time_start) / t_ramp
        x = 0
        b = step_time_start
        steps = 0
        x_y = []
        
        while x < t_ramp:
            now = ticks_us()
            x = now - t_start
            y = int(m * x + b)
            self.stp.value(1)
            sleep_us(y)
            self.stp.value(0)
            sleep_us(y)
            steps += 1
            if steps % 10 == 0:
                x_y.append([x, y])
        return [steps, x_y]
    
    def steps_pwm(self, freq, on_time):
        self.pwm.duty_u16(32768)
        self.pwm.freq(freq)
        sleep_ms(on_time)
        self.pwm.deinit()
        
    def ramp_pwm(self, freq_start, freq_end, pause):
        self.pwm.duty_u16(32768)
        freq = freq_start
        while freq < freq_end:
            self.pwm.freq(freq)
            sleep_ms(pause)
            freq += 200
        #self.pwm.deinit()
            
    
    def ramp_step_forecast(self, step_time_start, step_time_end, ramp_time):
        """
        Calculates the number of required steps for a ramp, resulting of the given parameters:
        step_time_start (in us) to step_time_end (in us) within the ramp_time (in ms).
        """
        t_ramp = ramp_time * 1000
        steps = 0.5 * t_ramp / step_time_start + 0.25 * t_ramp * ( 1 / step_time_end - 1 / step_time_start)
        return int(steps)
            
        
if __name__ == "__main__":
    #steps = 40000
    stepper_pul = Pin(2)
    stepper_dir = Pin(3)
    stepper_en = Pin(4)
    stepper_pwm = Pin(5)
    m1 = Stepper(stepper_pul, stepper_dir, stepper_en, stepper_pwm)
    #m1.step_time = 50
    #steps_calc = m1.ramp_step_forecast(500, m1.step_time, 1000)
    #results_from_ramp = m1.ramp(500, m1.step_time, 1000)
    #steps_actual = results_from_ramp[0]
    #ramp_x_y = results_from_ramp[1]
    #print("calculated steps: ", steps_calc)
    #print("actual steps: ", steps_actual)
    #m1.steps(steps - steps_ramp)
    
    #m1.steps_pwm(1000, 2000)
    freq_end = 20000
    m1.ramp_pwm(800, freq_end, 200)
    m1.steps_pwm(freq_end, 5000)
    #m1.steps(-40000)
#     data = ""
#     for i in ramp_x_y:
#         data += str(i[0]) + "," + str(i[1]) + "\r\n"
#     f = open('data.csv', 'w')
#     f.write(data)
#     f.close()