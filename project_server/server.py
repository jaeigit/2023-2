import socket
import RPi.GPIO as GPIO
import time

############################ GPIO setting ############################

# BCM pins	# BOARD num. 홀수 = 왼쪽, 짝수 = 오른쪽
TRIG = 23	# pin16
ECHO = 24	# pin18

# GPIO setting
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

########################### socket setting ###########################

# 접속할 서버 주소. localhost 사용
HOST = '192.168.233.157'

# 클라이언트 접속 대기 포트 번호
PORT = 9999        

# 소켓 객체 생성
# 주소 체계(address family)로 IPv4, 소켓 타입으로 TCP 사용 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 포트 사용중이라 연결할 수 없다는 WinError 10048 에러 해결를 위해 필요
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind 함수: 소켓을 특정 네트워크 인터페이스와 포트 번호에 연결하는데 사용
# HOST는 hostname, ip address, 빈 문자열 ""이 될 수 있습니다.
# 빈 문자열이면 모든 네트워크 인터페이스로부터의 접속 허용 
# PORT는 1-65535 사이의 숫자를 사용할 수 있습니다.  
server_socket.bind((HOST, PORT))

# 서버가 클라이언트의 접속을 허용
server_socket.listen()

# accept 함수에서 대기하다가 클라이언트가 접속하면 새로운 소켓을 리턴 
client_socket, addr = server_socket.accept()

# 접속한 클라이언트의 주소
print('Connected by', addr)

############################### function ###############################

def tmp(sign):
    sending = '0'

    # check sit or leave
    if sign == True:
        sending = "User Sit."

    elif sign == False:
        sending = "Nobody is there."

    else:
        print("sign error, "+sign+", "+sending)

    # send and receive
    # No change
    if sit == sit_tmp:
        return

    # Changed
    else:
        print("\n"+sending)
        time.sleep(0.01)
        client_socket.send(sending.encode())
        print("Sent \'"+sending+"\'!!!\n")
        print("I'm waiting client...\n")
        data = client_socket.recv(1024)
        string = data.decode()
        if string == "True":
            print("I received \'"+string+"\'.\n")

        elif string == "False":
            print("I received \'"+string+"\'...\n")

        elif string == "Finished!":
            print("I received \'"+string+"\'!!!\n")

        else:
            print("What? "+string)
            return

################################ main ################################

string = '0'
sit_tmp = sit = False

# 감지 시작
try:
    print("Start")
    
    # micro output reset
    GPIO.output(TRIG, False)

    # 센서 신호 대기 중
    print("Waiting for sensor to settle")
    time.sleep(0.1)

    while True:
        # 기본 설정
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        # 거리 측정
        while GPIO.input(ECHO)==0:
            start = time.time()

        while GPIO.input(ECHO)==1:
            stop = time.time()

        time.sleep(0.3)

        # 거리 계산
        check_time = stop - start
        distance = check_time * 34300 / 2

        # 일정 거리 이내 감지 = 착석
        if distance < 20:
            sit = True
            tmp(sit)
            
	    # 일정 거리 이상 = 이탈
        else:
            sit = False
            tmp(sit)

        sit_tmp = sit
        print("Waiting the change......")

        # rest
        time.sleep(0.01)

# Error Except	
except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()

# 소켓을 닫음
client_socket.close()
server_socket.close()