# Example file
import pygame, serial; from time import perf_counter

# pygame setup
pygame.init()
running = True

pygame.joystick.init()
joysticks = []

screen = pygame.display.set_mode((320, 200))
screen.fill((15, 15, 15))  # RGB fill
pygame.display.flip()  # update screen
pygame.display.set_caption("Input Window")

# serial setup
ser = serial.Serial(port='COM4', baudrate=115200)  # open serial port @ 115200 baud
print("Serial port: " + ser.name + "\nBaud: " + str(ser.baudrate))  # check which port and baud was really used

prev_Speed_L = 0
prev_Dir_L = 0
prev_Speed_R = 0
prev_Dir_R = 0


while running:
	# poll for events
	# pygame.QUIT event means the user clicked X to close your window
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			ser.close()  # close connection before killing
			running = False
		elif event.type == pygame.JOYDEVICEADDED:  # controller hotplugging handler
			print(f"New controller detected")
			joy = pygame.joystick.Joystick(event.device_index)
			joysticks.append(joy)

		### joystick buttons ###
		if event.type == pygame.JOYBUTTONDOWN:
			match event.button:
				case 5:  # PS, kill motors
					packet = bytes([0xFF, 0x00])
				case 11:  # D-pad up, led on
					packet = bytes([0xFF, 0x03, 0xFF])
				case 12:  # D-pad down, led off
					packet = bytes([0xFF, 0x03, 0x00])
					
			ser.write(packet)


	for joystick in joysticks:
		leftStick = joystick.get_axis(1)  # left stick y
		rightStick = joystick.get_axis(3)  # right stick y

		## left stick ##
		if abs(leftStick) > 0.05:  # ignore deadspace
			target_Speed_L = round(abs(leftStick * 255))  # map joystick to pwm
			target_Dir_L = 0 if leftStick < 0 else 1  # negative axis means reverse direction
		else:
			target_Speed_L = 0
			target_Dir_L = 0

		if (prev_Speed_L != target_Speed_L) or (prev_Dir_L != target_Dir_L):  # only update on change
			packet = bytes([0xFF, 0x04, target_Dir_L, target_Speed_L])  # motor0, joystick map
			ser.write(packet)
			prev_Speed_L = target_Speed_L
			prev_Dir_L = target_Dir_L
			
		## right stick ##	
		if abs(rightStick) > 0.05:  # ignore deadspace
			target_Speed_R = round(abs(rightStick * 255))  # map joystick to pwm
			target_Dir_R = 0 if rightStick < 0 else 1  # negative axis means reverse direction
		else:
			target_Speed_R = 0
			target_Dir_R = 0

		if (prev_Speed_R != target_Speed_R) or (prev_Dir_R != target_Dir_R):  # only update on change
			packet = bytes([0xFF, 0x05, target_Dir_R, target_Speed_R])  # motor1, joystick map
			ser.write(packet)
			prev_Speed_R = target_Speed_R
			prev_Dir_R = target_Dir_R
		


	### keyboard controls ###
	keys = pygame.key.get_pressed()
	if keys[pygame.K_q]:  # send packet over serial
		packet = bytes([0xFF, 0x04, 0x01, 0xFF])  # motor0, forwards, full speed
		ser.write(packet)
			
	if keys[pygame.K_a]:
		packet = bytes([0xFF, 0x04, 0x00, 0xFF])  # motor0, reverse, full speed
		ser.write(packet)

	if keys[pygame.K_w]:
		packet = bytes([0xFF, 0x04, 0x00, 0x00])  # motor0, brake
		ser.write(packet)
	
	if keys[pygame.K_e]:
		packet = bytes([0xFF, 0x05, 0x01, 0xFF])  # motor1, forwards, full speed
		ser.write(packet)
	
	if keys[pygame.K_d]:
		packet = bytes([0xFF, 0x05, 0x00, 0xFF])  # motor1, reverse, full speed
		ser.write(packet)

	if keys[pygame.K_s]:
		packet = bytes([0xFF, 0x05, 0x00, 0x00])  # motor1, brake
		ser.write(packet)
		
	if keys[pygame.K_SPACE]:
		packet = bytes([0xFF, 0x04, 0x00, 0x00])  # both motors, brake
		ser.write(packet)
		packet = bytes([0xFF, 0x05, 0x00, 0x00])
		ser.write(packet)

	if keys[pygame.K_z]:
		packet = bytes([0xFF, 0x03, 0xFF])  # led, on
		ser.write(packet)

	if keys[pygame.K_x]:
		packet = bytes([0xFF, 0x03, 0x00])  # led, off
		ser.write(packet)

pygame.quit()