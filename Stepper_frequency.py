"""Micropython module for stepper motor driven by Easy Driver."""
from machine import Pin
from utime import sleep_us, sleep_ms, sleep, ticks_us, ticks_ms

class Stepper:
    """Class for stepper motor driven by Easy Driver."""

    def __init__(self, step_pin, dir_pin, sleep_pin, rpm_hi, rpm_lo, ramp_up_time, ramp_dn_time, steps_per_rev):
        """
        Initialise stepper
        
        step_pin, dir_pin, sleep_pin: machine.Pin
        rpm_hi, rpm_lo: float
        ramp_up_time, ramp_dn_time: int (ms)
        steps_per_rev)
        """
        self.stp = step_pin
        self.dir = dir_pin
        self.slp = sleep_pin
        self.stop = Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)

        self.stp.init(Pin.OUT)
        self.dir.init(Pin.OUT)
        self.slp.init(Pin.OUT)

        self.set_direction()
        self.ramp_down = False
        
        self.freq_hi = steps_per_rev * rpm_hi / 60  # Hz
        self.freq_lo = steps_per_rev * rpm_lo / 60  # Hz
        self.half_period_hi = int(5e5 / self.freq_hi) # half period time in us for freq_hi
        self.half_period_lo = int(5e5 / self.freq_lo) # half period time in us for freq_lo
        self.steps_per_rev = steps_per_rev
        
#         self.ramp_correction_factor_hi = 1.2 # for 1500 rpm with 800 steps per revolution
#         self.ramp_correction_factor_lo = 1.06 # for 600 rpm with 800 steps per revolution
        self.ramp_correction_factor = 1.00 # values of ramp correction are calculated wrongly without this factor
        self.ramp_up = self.calc_ramp(self.freq_lo, self.freq_hi, ramp_up_time)
        if self.ramp_down:
            self.ramp_dn = self.calc_ramp(self.freq_hi, self.freq_lo, ramp_dn_time)
        else:
            self.ramp_dn = None
    
    def power_on(self):
        """Power on stepper."""
        self.slp.value(1)

    def power_off(self):
        """Power off stepper."""
        self.slp.value(0)
    
    def set_direction(self, right = True):
        self.turn_right = right
        self.dir.value(0 if right == True else 1)

    def do_revolutions(self, revolutions):
        """Rotate stepper motor for the given number of revolutions"""
        number_of_performed_steps = 0
        performed_steps_up = 0
        performed_steps_const = 0
        performed_steps_dn = 0
        
        self.set_direction(True if revolutions >= 0 else False)
        
        steps = abs(self.revolutions_to_steps(revolutions))
        if self.ramp_dn:
            steps_without_ramp = steps - len(self.ramp_up) - len(self.ramp_dn)
        else:
            steps_without_ramp = steps - len(self.ramp_up)
        
        if steps != 0:            
            if steps_without_ramp > 0: # enough steps for higher speed and ramps
                performed_steps_up = self.execute_ramp(self.ramp_up)
                performed_steps_const = self.execute_steps(steps_without_ramp, self.half_period_hi)
                if self.ramp_dn:
                    performed_steps_dn = self.execute_ramp(self.ramp_dn)
            else: # not enough steps for higher speed and ramps
                performed_steps_const = self.execute_steps(steps, self.half_period_lo)
            number_of_performed_steps = (performed_steps_up + performed_steps_const + performed_steps_dn) * (1 if self.turn_right else -1)
        return number_of_performed_steps
    
    def revolutions_to_steps(self, revolutions):
        return int(self.steps_per_rev * revolutions)
    
    def steps_to_revolutions(self, steps):
        return steps / self.steps_per_rev
    
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

    def calc_ramp(self, freq_start, freq_end, ramp_time):
        """
        Calculates a ramp from freq_start (in Hz) to freq_end (in Hz) within the ramp_time (in ms).
        
        Returns:
        A list of integers of half period times (in us) from freq_start to freq_end
        """
        
        t_ramp = ramp_time * 1000
        m = (freq_end - freq_start) / t_ramp
        b = freq_start
        x = 0
        correction = self.ramp_correction_factor
        half_period_times = []
        
        while x < t_ramp:
            # calculating half period time in us
            y = 5e5 / (m * x + b) * correction
            half_period_times.append(int(y))
            x += 2 * y 
        return half_period_times
    
    def execute_ramp(self, half_period_times):
        """
        Executes a ramp with a list of [x, y] with x from start of ramp_time to end of ramp_time and y from step_freq_start to step_freq_end
        """
        
        for index, half_period_time in enumerate(half_period_times):
            if self.stop.value() == 0:
                return index # number of performed steps
            self.stp.value(1)
            sleep_us(half_period_time)
            self.stp.value(0)
            sleep_us(half_period_time)
            #if self.turn_right:
            #    self.current_steps +=1
            #else:
            #    self.current_steps -=1
        return len(half_period_times)
    
    def execute_steps(self, steps, half_period_time):
        for i in range(steps):
            if self.stop.value() == 0:
                return i            
            self.stp.value(1)
            sleep_us(half_period_time)
            self.stp.value(0)
            sleep_us(half_period_time)
        return steps
        
        
if __name__ == "__main__":
    stepper_pul = Pin(2)
    stepper_dir = Pin(3)
    stepper_en = Pin(4)
    # def __init__(self, step_pin, dir_pin, sleep_pin, rpm_hi, rpm_lo, ramp_up_time, ramp_dn_time, steps_per_rev)
    m1 = Stepper(stepper_pul, stepper_dir, stepper_en, 600, 50, 1000, 400, 800)
    print(m1.do_revolutions(-100))
    
    
    #m1.steps(9000)
    #m1.ramp(800, m1.step_freq, 3000)
    #m1.steps(10000)
    #steps_calc = m1.ramp_step_forecast(500, m1.step_time, 1000)
    #results_from_ramp = m1.ramp(400, m1.step_freq, 500)
    #steps_actual = results_from_ramp[0]
    #ramp_x_y = results_from_ramp[1]
    #print("calculated steps: ", steps_calc)
    #print("actual steps: ", steps_actual)
    #m1.steps(steps - steps_ramp)
    
    #m1.steps(-40000)
#     data = ""
#     for i in ramp_x_y:
#         data += str(i[0]) + "," + str(i[1]) + "\r\n"
#     f = open('data.csv', 'w')
#     f.write(data)
#     f.close()