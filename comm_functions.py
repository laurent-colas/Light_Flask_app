import constant as const
import Adafruit_PCA9685
# import RPi.GPIO as GPIO
# import smbus

# bus = smbus.SMBus(1)
# GPIO.setmode(GPIO.BCM)

# pwm = Adafruit_PCA9685.PCA9685()
# pwm_freq = 500
# pwm.set_pwm_freq(pwm_freq)

def string_to_bytes(val):
    ret_val = []
    for c in val:
        ret_val.append(ord(c))
    return ret_val

def write_number(relay_address, value):
    bus.write_byte(relay_address, value)
    return -1


def send_light_state(adresse, brightness):
    if adresse[0] == "A":
        send_pwm_light_state(adresse, brightness)
    else:
        send_relay_light_state(adresse, brightness)



def send_pwm_light_state(adresse, brightness):
    address_num = int(adresse[1:])
    if address_num < 16:
        pwm_address = const.address_pwm_1
    elif address_num >= 15 and address_num < 32:
        pwm_address = const.address_pwm_2
    elif address_num > 31 and address_num < 48:
        pwm_address = const.address_pwm_3
    elif address_num > 47 and address_num < 64:
         pwm_address = const.address_pwm_4
    pwm_brightness_off = int((int(brightness) / 100) * 4095)
    # pwm.set_pwm(address_num, 0, pwm_brightness_off)

def send_relay_light_state(adresse, brightness):
    command = create_relay_string(address, brightness)


def create_relay_string(address, brightness):
    if brightness <= 10:
        brightness = 0
    else:
        brightness = 1
    command = address + " " + brightness
    return command
