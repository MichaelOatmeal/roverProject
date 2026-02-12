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
ser = serial.Serial(port='COM3', baudrate=115200)  # open serial port @ 115200 baud
print(ser.name)         # check which port was really used

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ser.close()
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        ser.write(b'w')
        print("w")
    if keys[pygame.K_s]:
        ser.write(b's')
        print("s")
    if keys[pygame.K_a]:
        ser.write(b'a')
        print("a")
    if keys[pygame.K_d]:
        ser.write(b'd')
        print("d")

pygame.quit()