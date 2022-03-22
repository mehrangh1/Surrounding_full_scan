import RPi.GPIO as GPIO 
import time
import numpy as np
import matplotlib.pyplot as plt
import smtplib
import statistics
import datetime

timestr = time.strftime("%Y%m%d-%H%M%S")

GPIO.setmode(GPIO.BOARD)
distance_data = np.zeros((10,4))
pin_map_list = [[3,13,15],[7,16,18],[8,19,21],[11,22,23]] #modify the arrays in case using other pins on the raspberry pi

def setup_pins(pin_map):
    for pin_group in pin_map:
        GPIO.setup(pin_group[0], GPIO.OUT) #servo output
        GPIO.setup(pin_group[1], GPIO.OUT) #sensor output
        GPIO.setup(pin_group[2], GPIO.IN) #sensor input
        print("PIN Initialized Servo pin:%s\nRange out pin:%s\nRange in pin:%s")
    print("All pins are initialized")

def range_finder(range_pin_out, range_pin_in):
    GPIO.output(range_pin_out,True)
    time.sleep(0.00001)
    GPIO.output(range_pin_out,False)
    while GPIO.input(range_pin_in) == 0:
        pulse_start = time.time()
    while GPIO.input(range_pin_in) == 1:
        pulse_stop = time.time()
    pulse_duration = pulse_stop - pulse_start
    distance = pulse_duration * 17150 #speed of voice /2 
    d = round(distance,2)
    print ("Distance:" ,d, "cm")
    return d

def scan_all(pin_map, sensor_num = 0):
    for sensor_pair in pin_map:
        servo_pin = sensor_pair[0]
        range_pin_out = sensor_pair[1]
        range_pin_in = sensor_pair[2]
        pwm = GPIO.PWM(servo_pin, 50) #frequency
        pwm.start(5)
        print("Servo pin:%s\nRange out pin:%s\nRange in pin:%s")
        for i in range(0,80,8): # 80 cuz the servo i used was not calibrated 
            DC = 1./18.*(i)+2
            pwm.ChangeDutyCycle(DC)
            time.sleep(.3)
            distance = range_finder(range_pin_out, range_pin_in)
            distance_data[int(i/8)-1, sensor_num] = distance
            time.sleep(.3)
        sensor_num +=1
    
    for i in range(1,5):
        theta = np.range((i-1)/2*np.pi, (i)/2*np.pi, 1/20*np.pi)
        r = distance_data[:, (i-1)]
        ax = plt.subplot(220+i, projection="polar")        
        ax.plot(theta, r)
        ax.set_thetamax(i*90)
        ax.set_thetamin((i-1)*90)
        ax.set_rmax(35)
    plt.savefig("fig1.png")
    np.savetxt(str(datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"), np.asarray(distance_data), delimiter = ",")

setup_pins(pin_map_list)
scan_all(pin_map_list)
print(distance_data)

mean1 = statistics.mean(distance_data[:,0])
mean2 = statistics.mean(distance_data[:,1])
mean3 = statistics.mean(distance_data[:,2])
mean4 = statistics.mean(distance_data[:,3])

SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = 'youremail@email.com' #change this to match your gmail account
GMAIL_PASSWORD = 'yourPassword' #change this to match your gmail password

class Emailer:
    def sendmail(self, recipient, subject, content):

#Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
        "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)

#Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

#Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

#Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit

sender = Emailer()

if mean1 and mean2 and mean3 and mean4 <10:
    sendTo = "recipient email address"
    emailSubject = "Container"
    emailContent = "Objects are relatively close to the sensors"
    sender.sendmail(sendTo, emailSubject, emailContent)
    print("Email Sent!")




