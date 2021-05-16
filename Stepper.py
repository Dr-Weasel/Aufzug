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
        self.period_hi = int(1e6 / self.freq_hi) # half period time in us for freq_hi
        self.period_lo = int(1e6 / self.freq_lo) # half period time in us for freq_lo
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
                performed_steps_const = self.execute_steps(steps_without_ramp, self.period_hi)
                if self.ramp_dn:
                    performed_steps_dn = self.execute_ramp(self.ramp_dn)
            else: # not enough steps for higher speed and ramps
                performed_steps_const = self.execute_steps(steps, self.period_lo)
            number_of_performed_steps = (performed_steps_up + performed_steps_const + performed_steps_dn) * (1 if self.turn_right else -1)
        return number_of_performed_steps
    
    def revolutions_to_steps(self, revolutions):
        return int(self.steps_per_rev * revolutions)
    
    def steps_to_revolutions(self, steps):
        return steps / self.steps_per_rev
    
    def calc_ramp(self, freq_start, freq_end, ramp_time):
        """
        Calculates a ramp from freq_start (in Hz) to freq_end (in Hz) within the ramp_time (in ms).
        
        Returns:
        A list of integers of period times (in us) from freq_start to freq_end
        """
        
        t_ramp = ramp_time * 1000
        m = (freq_end - freq_start) / t_ramp
        b = freq_start
        x = 0
        correction = self.ramp_correction_factor
        period_times = []
        
        while x < t_ramp:
            # calculating half period time in us
            y = 1e6 / (m * x + b) * correction
            period_times.append(int(y))
            x += 2 * y 
        return period_times
    
    def execute_ramp(self, period_times):
        """
        Executes a ramp with a list of period times from freq_start to freq_end
        """
        for index, period_time in enumerate(period_times):
            before_if = ticks_us()
            if self.stop.value() == 0 or self.stop.value() == 0 or self.stop.value() == 0:
                return index # number of performed steps
            after_if = ticks_us()
            self.stp.value(1)
            sleep_us(1)
            self.stp.value(0)
            sleep_us(period_time + before_if - after_if - 1)
        return len(period_times)
    
    def execute_steps(self, steps, period_time):
        for i in range(steps):
            before_if = ticks_us()
            if self.stop.value() == 0 or self.stop.value() == 0 or self.stop.value() == 0:
                return i
            after_if = ticks_us()
            self.stp.value(1)
            sleep_us(1)
            self.stp.value(0)
            sleep_us(period_time + before_if - after_if - 1)
        return steps
        
        
if __name__ == "__main__":
    stepper_pul = Pin(2)
    stepper_dir = Pin(3)
    stepper_en = Pin(4)
    # def __init__(self, step_pin, dir_pin, sleep_pin, rpm_hi, rpm_lo, ramp_up_time, ramp_dn_time, steps_per_rev)
    m1 = Stepper(stepper_pul, stepper_dir, stepper_en, 600, 50, 1200, 400, 800)
    for i in range(10):
        m1.do_revolutions(4)
        sleep_ms(50)
        m1.do_revolutions(-4)
        sleep_ms(50)
    