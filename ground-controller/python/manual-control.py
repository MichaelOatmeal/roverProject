# TODO: 
# split into nicer functions - better grouping!
# test controller inputs

'''
| Direction     | Category  | Message ID | Content                                           |
| ------------- | --------- | ---------- | ------------------------------------------------- |
| Pi -> Arduino | Admin     | 0x00       | Emergency state X - run routine and await command |
|               |           | 0x01       | Exit emergency state                              |
|               |           | 0x02       | Toggle verbose telemetry                          |
|               |           | 0x03       | Toggle audio alerts                               |
|               |           | 0x04       | Debug 1 (eg live PID)                             |
|               |           | 0x05       | Debug 2 (eg live PID)                             |
|               | Command   | 0x10       | Move motors                                       |
|---------------|-----------|------------|---------------------------------------------------|
| Arduino -> Pi | Admin     | 0x80       | Error (eg missing expected component)             |
|               | Telemetry | 0x90       | Motors RPM                                        |
|               |           | 0x91       | Motors voltage                                    |
|               |           | 0x92       | Motors current                                    |
|               |           | 0x93       | Encoder counts (verbose)                          |
|               |           | 0xA0       | Battery voltage and current                       |
|               |           | 0xA1       | Battery temperature                               |
|               |           | 0xB0       | Raw IMU                                           |
|               |           | 0xB1       | Raw GNSS                                          |
|---------------|-----------|------------|---------------------------------------------------|
| Bidirectional | Admin     | 0xFE       | Heartbeat                                         |
'''

# Example file
import pygame, serial, time, queue, struct, threading, traceback
import serial.tools.list_ports

# pygame setup
pygame.init()
running = True
clock = pygame.time.Clock()

pygame.joystick.init()
joysticks = []
SHEIGHT = 400
SWIDTH = 640
screen = pygame.display.set_mode((SWIDTH, SHEIGHT))
screen.fill((100, 100, 100))  # RGB fill
pygame.display.flip()  # update screen
pygame.display.set_caption("Input Window")

font = pygame.font.SysFont("Calibri", 20)

text1 = font.render('W = Forwards, S = Backwards', False, (255,255,255), (70,70,70))
textRect1 = text1.get_rect()
textRect1.center = (480, 60)

text2 = font.render('A = Sweep Left, D = Sweep Right', False, (255,255,255), (70,70,70))
textRect2 = text2.get_rect()
textRect2.center = (493, 40)

text3 = font.render('Q = Pivot Left, E = Pivot Right', False, (255,255,255), (70,70,70))
textRect3 = text3.get_rect()
textRect3.center = (480, 20)

bgRect = pygame.Rect(360, 0, 300, (textRect1.height+textRect2.height+textRect3.height)+20)

hud = pygame.Surface((SWIDTH, SHEIGHT), pygame.SRCALPHA)
pygame.draw.rect(hud, (70,70, 70), bgRect)

sAccelText = font.render("Accelerometer:", False, (255,255,255))
sGyroText = font.render("Angular Velocity:", False, (255,255,255))
sMagText = font.render("Magnetometer:", False, (255,255,255))
sTempText = font.render("Temperature:", False, (255,255,255))

hud.blit(sAccelText, (360, 100))
hud.blit(sGyroText, (360, 120))
hud.blit(sMagText, (360, 140))
hud.blit(sTempText, (360, 160))

hud.blit(text1, textRect1)
hud.blit(text2, textRect2)
hud.blit(text3, textRect3)

### serial setup ###

rx_buffer = bytearray()
serial_thread = None
serial_Queue = queue.Queue()
prev_Packet_Out = None
header = 0
heartbeat1 = 0
packet_sequence = 0
awaiting_ACK = False
dropped_Packets = 0
serial_Raw: serial.Serial | None = None

while serial_Raw == None:  # search for arduino
  all_Ports = serial.tools.list_ports.comports()	# get all open serial ports
  for comport in all_Ports:
    if ("arduino" in comport.description.lower() 
      or comport.device.startswith("/dev/ttyUSB") 
      or comport.device.startswith("/dev/ttyACM")):

      serial_Raw = serial.Serial(port=comport.device, baudrate=230400, timeout=0.1, write_timeout=0.1)  # open serial port @ 115200 baud
      print(f"Serial port: {serial_Raw.name or 'unknown'}\nBaud: {serial_Raw.baudrate}")  # print which port and baud was really used
      time.sleep(2); serial_Raw.reset_input_buffer(); serial_Raw.reset_output_buffer()
      break

  if serial_Raw == None: print("No port available")

## packet sizes ##

MOTOR_DATA_FORMAT = "<hh"
MOTOR_DATA_SIZE = struct.calcsize(MOTOR_DATA_FORMAT)
MOTOR_RESERVED_SIZE = 16 - MOTOR_DATA_SIZE

ACCEL_DATA_FORMAT = "<fff"
ACCEL_DATA_SIZE = struct.calcsize(ACCEL_DATA_FORMAT)
ACCEL_RESERVED_SIZE = 16 - ACCEL_DATA_SIZE

GYRO_DATA_FORMAT = "<fff"
GYRO_DATA_SIZE = struct.calcsize(GYRO_DATA_FORMAT)
GYRO_RESERVED_SIZE = 16 - GYRO_DATA_SIZE

MAG_DATA_FORMAT = "<fff"
MAG_DATA_SIZE = struct.calcsize(MAG_DATA_FORMAT)
MAG_RESERVED_SIZE = 16 - MAG_DATA_SIZE

TEMP_DATA_FORMAT = "<3sf"
TEMP_DATA_SIZE = struct.calcsize(TEMP_DATA_FORMAT)
TEMP_RESERVED_SIZE = 16 - TEMP_DATA_SIZE

HBEAT_DATA_FORMAT = "<"
HBEAT_DATA_SIZE = struct.calcsize(HBEAT_DATA_FORMAT)
HBEAT_RESERVED_SIZE = 16 - HBEAT_DATA_SIZE

CRC_SIZE = 1

## input values ##
motor0_RPM = 0.0
motor1_RPM = 0.0

imu_Accel = [0, 0, 0]
imu_Gyro = [0, 0, 0]
imu_Mag = [0, 0, 0]
imu_Temp = 0.0




def crc8(data):
  crc = 0x00

  for byte in data:
    crc ^= byte

    for _ in range(8):
      if crc & 0x80:
        crc = ((crc << 1) ^ 0x07) & 0xFF
      else:
         crc = (crc << 1) & 0xFF

  return crc

def crc8Validate(crc8_val, data):
  rcvSum = crc8(data)

  if isinstance(crc8_val, bytes):  # avoid comparing bytes to int
    crc8_val = crc8_val[0]

  return rcvSum == crc8_val


def out_Handler_MOT_IN(data: bytes):
  rpm0, rpm1 = struct.unpack("<hh", data[:4])
  return make_motor_packet(rpm0, rpm1)

def make_motor_packet(rpm0, rpm1):
  global packet_sequence

  sequence = packet_sequence
  packet_sequence = (packet_sequence + 1) & 0xFF
  data = struct.pack(MOTOR_DATA_FORMAT, rpm0, rpm1)

  packet = (
    b'\x10'
    + bytes([sequence])
    + data
    + b'\x00' * MOTOR_RESERVED_SIZE
  )

  return packet + bytes([crc8(packet)])


def out_Handler_HBEAT():
  return make_heartbeat_packet()

def make_heartbeat_packet():
  global packet_sequence

  sequence = packet_sequence
  packet_sequence = (packet_sequence + 1) & 0xFF

  packet = (
    b'\xFE'
    + bytes([sequence])
    + b'\x00' * HBEAT_RESERVED_SIZE
  )

  return packet + bytes([crc8(packet)])


packet_ID_dict: dict[str, int] = {
  "EMG":     0x01,
  "ERR":     0x02,
  "MOT_IN":  0x10,
  "MOT_OUT": 0x11,
  "ACCEL":   0x20,
  "MAG":		 0x21,
  "GYRO":    0x22,
  "BATT_IV": 0x30,
  "TEMP":    0x31,
  "HBEAT":   0xFE,
}

outgoing_Handlers = {
  packet_ID_dict["MOT_IN"]: out_Handler_MOT_IN,
  packet_ID_dict["HBEAT"]:  out_Handler_HBEAT,
}

def make_packet(id: bytes, data: bytes):
  handler = outgoing_Handlers.get(int(id))

  if handler is not None:
    packet = handler(data)
    serial_Queue.put_nowait(packet)
  else:
    raise ValueError(f"Unknown packet ID: {id!r}")

def outgoing_Write():
  global heartbeat1

  if serial_Raw is None:  # verify connection
    raise RuntimeError("Serial connection is not available!")

  try:
    packet_Out = serial_Queue.get_nowait()
  except queue.Empty:
    return

  serial_Raw.write(b'\xAA')
  serial_Raw.write(packet_Out)
  serial_Raw.write(b'\x55')
  # print("Sent this:", packet_Out)

  heartbeat1 = time.perf_counter()

def heartbeat():
  global heartbeat1, awaiting_ACK
  now = time.perf_counter()  # time now in ms

  if serial_Raw is None:
    raise RuntimeError("Serial connection is not available!")

  if now - heartbeat1 > 0.5:  # send heartbeat after 0.5s with no command sent
    serial_Raw.write(b'\xAA')  # header
    serial_Raw.write(make_heartbeat_packet())
    serial_Raw.write(b'\x55')  # delimiter
    heartbeat1 = time.perf_counter()
    awaiting_ACK = True

def serialSendUrgent(packet_Out):  # drain the queue
  while not serial_Queue.empty():
    try: serial_Queue.get_nowait()
    except queue.Empty: break
  serial_Queue.put(packet_Out)

def incoming_Read():
  global rx_buffer

  if serial_Raw is None:
    raise RuntimeError("Serial connection is not available!")

  # Read everything currently available
  if serial_Raw.in_waiting:
    rx_buffer.extend(serial_Raw.read(serial_Raw.in_waiting))

  PACKET_SIZE = 19
  FRAME_SIZE = 21   # AA + 19-byte packet + 55

  while True:

    # Find start delimiter
    try:
      start = rx_buffer.index(0xAA)
    except ValueError:
      rx_buffer.clear()
      return None

    # Throw away anything before AA
    if start > 0:
      del rx_buffer[:start]

    # Wait until entire frame has arrived
    if len(rx_buffer) < FRAME_SIZE:
      return None

    # Check end delimiter
    if rx_buffer[20] != 0x55:
      print("bad delim!")

      # Discard this AA and try to find next one
      del rx_buffer[0]
      continue

    # Extract the 19-byte packet
    packet_In_Full = bytes(rx_buffer[1:20])

    # Remove complete frame from buffer
    del rx_buffer[:21]

    return packet_In_Full

def incoming_Parse(packet_In_Full):
  global awaiting_ACK, heartbeat1, motor0_RPM, motor1_RPM
  global packet_In_ID, packet_Sequence, packet_ID_dict, dropped_Packets
  global imu_Accel, imu_Temp, imu_Gyro, imu_Mag, imu_Temp_ID


  if packet_In_Full is None:
    return

  packet_In_ID = packet_In_Full[0]
  packet_Sequence = packet_In_Full[1]

  # Byte 18 is CRC
  packet_In_CRC8 = packet_In_Full[18]

  if not crc8Validate(packet_In_CRC8, packet_In_Full[:18]):
    dropped_Packets += 1
    print("Bad packet: invalid CRC")
    return

  if packet_In_ID == packet_ID_dict.get("MOT_OUT"):
    packet_In_Data = packet_In_Full[2:2+MOTOR_DATA_SIZE]
    motor0_RPM, motor1_RPM = struct.unpack('<hh', packet_In_Data)  # convert bytes from array to little-endian float
    print("Got:", motor0_RPM, motor1_RPM)
    
  elif packet_In_ID == packet_ID_dict.get("ACCEL"):
    packet_In_Data = packet_In_Full[2:2+ACCEL_DATA_SIZE]
    imu_Accel = struct.unpack('<fff', packet_In_Data)
    print("Accel!")

  elif packet_In_ID == packet_ID_dict.get("GYRO"):
    packet_In_Data = packet_In_Full[2:2+GYRO_DATA_SIZE]
    imu_Gyro = struct.unpack('<fff', packet_In_Data)
    print("Gyro!")
    
  elif packet_In_ID == packet_ID_dict.get("MAG"):
    packet_In_Data = packet_In_Full[2:2+MAG_DATA_SIZE]
    imu_Mag = struct.unpack('<fff', packet_In_Data)
    print("Mag!")
    
  elif packet_In_ID == packet_ID_dict.get("TEMP"):
    packet_In_Data = packet_In_Full[2:2+TEMP_DATA_SIZE]
    imu_Temp_ID, imu_Temp = struct.unpack('<3sf', packet_In_Data[:7])
    print("Temp!")
    
  elif packet_In_ID == packet_ID_dict.get("HBEAT"):
    awaiting_ACK = False
    print("beat")

def pygame_Poll():
  global running
  for event in pygame.event.get():
    if event.type == pygame.QUIT:  # window closed
      running = False

    ### keyboard controls ###
    elif event.type == pygame.KEYDOWN:  # send command once on key down
      match event.key:
        case pygame.K_w:
          packet = make_motor_packet(128, 128)
          serial_Queue.put_nowait(packet)

        case pygame.K_s:  # rev full
          packet = make_motor_packet(-128, -128)
          serial_Queue.put_nowait(packet)

        case pygame.K_a:  # sweep left
          packet = make_motor_packet(32, 128)
          serial_Queue.put_nowait(packet)

        case pygame.K_d:  # sweep right
          packet = make_motor_packet(128, 32)
          serial_Queue.put_nowait(packet)

        case pygame.K_q:  # pivot left
          packet = make_motor_packet(-128, 128)
          serial_Queue.put_nowait(packet)

        case pygame.K_e:  # pivot right
          packet = make_motor_packet(128, -128)
          serial_Queue.put_nowait(packet)

    elif event.type == pygame.KEYUP:  # send stop command on any key up
          packet = make_motor_packet(0, 0)
          serial_Queue.put_nowait(packet)

    elif event.type == pygame.JOYDEVICEADDED:  # controller hotplugging handler
      print(f"New controller detected")
      joy = pygame.joystick.Joystick(event.device_index)
      joysticks.append(joy)

    ### controller buttons ###
    
    # elif event.type == pygame.JOYBUTTONDOWN:
      # match event.button:
        # case 11:  # D-pad up
          # serial_Queue.put_nowait(b'\xAA\x03\xAA\x00\x00\x00')

        # case 12:  # D-pad down
          # serial_Queue.put_nowait(b'\xAA\x03\x00\x00\x00\x00')

    '''
    ###	joysticks	### deprecated

    for joystick in joysticks:
      leftStick = joystick.get_axis(1)  # left stick y
      rightStick = joystick.get_axis(3)  # right stick y

      ## left stick ##
      if abs(leftStick) > 0.03:  # ignore deadspace
        target_Speed_L = round(abs(leftStick * 255))  # map joystick to pwm
        target_Dir_L = 0 if leftStick < 0 else 1  # negative value means reverse direction
      else:
        target_Speed_L = 0
        target_Dir_L = 0

      if (prev_Speed_L != target_Speed_L) or (prev_Dir_L != target_Dir_L):  # only update on change
        serial_Queue.put_nowait(bytes([0xAA, 0x01, target_Dir_L, target_Speed_L]))  # motor0, joystick map
        prev_Speed_L = target_Speed_L
        prev_Dir_L = target_Dir_L
      
      ## right stick ##
      if abs(rightStick) > 0.03:  # ignore deadspace
        target_Speed_R = round(abs(rightStick * 255))  # map joystick to pwm
        target_Dir_R = 0 if rightStick < 0 else 1  # negative value means reverse direction
      else:
        target_Speed_R = 0
        target_Dir_R = 0

      if (prev_Speed_R != target_Speed_R) or (prev_Dir_R != target_Dir_R):  # only update on change
        serial_Queue.put_nowait(bytes([0xAA, 0x02, target_Dir_R, target_Speed_R]))  # motor1, joystick map
        prev_Speed_R = target_Speed_R
        prev_Dir_R = target_Dir_R
    '''
    

def imuValBlit(nameOfImuValue, y):
  count = 0
  x = 510
  colour = [255, 0, 0]
  while count != 3:
    nameOfVar = font.render(f"{nameOfImuValue[count]:.1f}", False, colour)
    screen.blit(nameOfVar, (x, y))
    x += 40
    if count < 2:
      colour[count+1] = colour[count]
      colour[count] = 0
    count += 1

def update_Graphics():
  global imu_Accel, imu_Temp, imu_Gyro, imu_Mag
  screen.fill((100, 100, 100))

  rpm0bgRect = pygame.Rect(10, 10, 100, 360)
  rpm1bgRect = pygame.Rect(180, 10, 100, 360)
  rpm0rect = pygame.Rect(10, 200 - motor0_RPM, 100, motor0_RPM)
  rpm1rect = pygame.Rect(180, 200 - motor1_RPM, 100, motor1_RPM)
  rpm0rect.normalize() #Flips direction of rectange if negative
  rpm1rect.normalize()
  

  pygame.draw.rect(screen, (70,70,70), rpm0bgRect)
  pygame.draw.rect(screen, (70,70,70), rpm1bgRect)

  #Bounding rpm rectangle within bg rectangle
  if rpm0rect.y < 0 and abs(rpm0rect.y) >= rpm0bgRect.y:
    rpm0rectnew = pygame.Rect(10, rpm0bgRect.top, 100, (motor0_RPM + (200-motor0_RPM)))
    pygame.draw.rect(screen, (255,0,0), rpm0rectnew)
  elif rpm0rect.bottom > rpm0bgRect.bottom:
    rpm0rectnew = pygame.Rect(10, 200, 100, 170)
    pygame.draw.rect(screen, (255,0,0), rpm0rectnew)
  else:
    pygame.draw.rect(screen, (255,0,0), rpm0rect)

  if rpm1rect.y < 0 and abs(rpm1rect.y) >= rpm1bgRect.y:
    rpm1rectnew = pygame.Rect(180, rpm1bgRect.top, 100, (motor1_RPM + (200-motor1_RPM)))
    pygame.draw.rect(screen, (255,0,0), rpm1rectnew)
  elif rpm1rect.bottom > rpm1bgRect.bottom:
    rpm1rectnew = pygame.Rect(180, 200, 100, 170)
    pygame.draw.rect(screen, (255,0,0), rpm1rectnew)
  else:
    pygame.draw.rect(screen, (255,0,0), rpm1rect)
    
  
  screen.blit(hud, (0, 0))

  rpm0_text = font.render(f"Motor0 RPM: {motor0_RPM:.1f}", False, (255, 255, 255))
  rpm1_text = font.render(f"Motor1 RPM: {motor1_RPM:.1f}", False, (255, 100, 100))
  imuValBlit(imu_Accel, 100)
  imuValBlit(imu_Gyro, 120)
  imuValBlit(imu_Mag, 140)
  
  imuTempVal_text = font.render(f"{imu_Temp:.1f}", False, (255, 255, 255))
  screen.blit(rpm0_text, (10, 380))
  screen.blit(rpm1_text, (180, 380))
  screen.blit(imuTempVal_text, (510, 160))
  
  pygame.display.flip()


def serialIO():
  global running  # allows these variables to be modified globally
  while running:
    time.sleep(0.001)
    ### serial control	###

    try: # serial access
      if serial_Raw is None:
        raise RuntimeError("Serial connection is not available!")

      ## heartbeat ##
      heartbeat()

      ## write serial ##
      outgoing_Write()

      ## read serial ##
      packet = incoming_Read()
      incoming_Parse(packet)

    except Exception as err:
      print("Serial error!:")
      print(type(err).__name__, err)
      traceback.print_exc()


### main loop ###

try:
  serial_thread = threading.Thread(target=serialIO, daemon=True)
  serial_thread.start()  # start threaded serial 

  while running:
  # poll for events
    pygame_Poll()

    if not running:
      break
  # Graphics (potato is temporary, absolute RPM)
    update_Graphics()
    clock.tick(60)

finally:
  running = False
  if serial_thread is not None:
    serial_thread.join()

  if serial_Raw is not None:
    serial_Raw.close()

  print("Closing safely...")
  pygame.quit()
