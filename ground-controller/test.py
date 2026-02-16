# Example file
import pygame, serial

# pygame setup
pygame.init()
running = True

screen = pygame.display.set_mode((320, 200))
screen.fill((15, 15, 15))  # RGB fill
pygame.display.flip()  # update screen
pygame.display.set_caption("Input Window")

# serial setup
ser = serial.Serial(port='COM4', baudrate=115200)  # open serial port @ 115200 baud
print("Serial port: " + ser.name + "\nBaud: " + str(ser.baudrate))  # check which port and baud was really used


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ser.close()  # close connection before killing
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:  # send packet over serial
        packet = bytes([0xFF, 0x01, 0xFF])  # led on
        ser.write(packet)
    if keys[pygame.K_s]:
        packet = bytes([0xFF, 0x01, 0x00])  # led off
        ser.write(packet)
    if keys[pygame.K_z]:
        packet = bytes([0x4A, 0x01, 0x00])  # bad header test
        ser.write(packet)
    if keys[pygame.K_x]:
        packet = bytes([0xFF, 0xB3, 0xFF])  # unused id test
        ser.write(packet)

pygame.quit()