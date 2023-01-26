from inputs import get_gamepad
import math
import threading
import serial
import time

#from using command -----  dmesg | tail -f
#ARDUINO_PORT = "/dev/ttyACM0"
ARDUINO_PORT = "COM3"

#ARDUINO_PORT = "COM4" # Should probably make this automatically look for the arduino in
              # the future, or at the very least make it fetch command line
              # argument.

class XboxController():
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):

        # Controller State variables:
        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        # Initialize the daemon thread which monitors the gamepad events
        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    # return the buttons/triggers we want to use
    # TODO: decide which buttons we want to use
    def read(self):
        x = self.LeftJoystickX
        y = self.LeftJoystickY
        a = self.A
        b = self.X
        c = self.Y
        d = self.B
        rb = self.RightBumper

        return [a, b, c, d, x, y]

    # Update the state varibles every time there is an event
    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                # if event.code is not "SYN_REPORT":
                #     print(event.code)

                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.Y = event.state
                elif event.code == 'BTN_WEST':
                    self.X = event.state
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state

                ''' NOTE: OUR TEST GAVE DIFFERENT CODE NAMES FOR DPAD
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state
                '''
# uses data from the gamepad to calculate motor power commands for the robot
# TODO: implement this
def motorPower(gamepadInputs):
    #print(gamepadInputs[0])
    return (gamepadInputs[0], gamepadInputs[5]) #reads "a": 1/0; reads left joystick y value

    #return [0,0,0,0,0,0] # (front left, front right, back left, back right,
                         #  up left, up right)
                         # ^ my suggested protocol for motor commands
                         # feel to interpret however.


def wait(ser, timeout):
    t = time.time()
    while ser.in_waiting == 0:
        if time.time() - t > timeout:
            print("wait timed out")
            break
    print("receive wait: " + str(time.time() - t) + "s")

#put the loop function in a big while loop with a try clause so the program automatically sleeps and restarts when an error is thrown
if __name__ == '__main__':
    # while True:
        #try:
    controller = XboxController()
    ser = serial.Serial(ARDUINO_PORT, 9600, timeout=0.01)

    time.sleep(1)

    while True:
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        raw = motorPower(controller.read())
        instructions = [raw[0], int(abs(raw[1] - 1) * 100)]
        if instructions[1] > 95 and instructions[1] < 105:
            instructions[1] = 100 #if controller is just on the edge don't move anything

        print("sending: " + str(instructions))

        ser.write(bytearray(instructions)) #write a bytearray that takes a list of integers from 0 to 255
        

        time.sleep(.05)
        
        wait(ser, 2) #waits for arduino response for up to 2 seconds

        response = ser.readline()
        print(response)

        # except:
        #     print("error detected, waiting 1 sec")
        #     time.sleep(1)
