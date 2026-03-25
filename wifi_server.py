import socket
import threading
import json
import time

# Importamos las clases de tu Freenove local
from motor import Ordinary_Car
from ultrasonic import Ultrasonic
from adc import ADC

# Inicializamos los componentes del hardware
try:
    motor = Ordinary_Car()
    ultrasonic = Ultrasonic()
    adc = ADC()
    print("Hardware inicializado correctamente.")
except Exception as e:
    print(f"Advertencia al inicializar el hardware: {e}")

HOST = '0.0.0.0' # Escucha en todas las interfaces de red
PORT = 65432     # Puerto por defecto para el lab

def handle_command(cmd):
    """
    Controla el movimiento del coche usando set_motor_model.
    Velocidad configurada a 1500 (el rango es de -4095 a 4095).
    """
    cmd = cmd.strip().lower()
    speed = 1500 
    
    if cmd == 'forward':
        motor.set_motor_model(speed, speed, speed, speed)
    elif cmd == 'backward':
        motor.set_motor_model(-speed, -speed, -speed, -speed)
    elif cmd == 'left':
        motor.set_motor_model(-speed, -speed, speed, speed)
    elif cmd == 'right':
        motor.set_motor_model(speed, speed, -speed, -speed)
    elif cmd == 'stop':
        motor.set_motor_model(0, 0, 0, 0)

def get_cpu_temp():
    """Lee la temperatura de la CPU de la Raspberry Pi."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000.0
            return round(temp, 1)
    except:
        return 0.0

def get_stats():
    """
    Recopila los datos de los sensores: Distancia, Batería y Temperatura CPU.
    """
    try:
        dist = ultrasonic.get_distance()
        bat_raw = adc.read_adc(2) * (3 if adc.pcb_version == 1 else 2)
        cpu_temp = get_cpu_temp()
        
        return json.dumps({
            "distance_cm": round(dist, 2),
            "battery_voltage": round(bat_raw, 2),
            "cpu_temp": cpu_temp,
            "status": "OK"
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def handle_client(conn, addr):
    print(f"Cliente conectado desde {addr}")
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                
                msg = data.decode('utf-8').strip()
                print(f"Recibido: {msg}")
                
                if msg == 'stats':
                    response = get_stats()
                    conn.sendall(response.encode('utf-8'))
                else:
                    handle_command(msg)
                    conn.sendall(b'Comando ejecutado')
            except ConnectionResetError:
                break
    
    # Detenemos el coche por seguridad si el cliente se desconecta
    motor.set_motor_model(0, 0, 0, 0)
    print(f"Cliente {addr} desconectado.")

# Configuración del servidor TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Servidor WiFi escuchando en el puerto {PORT}...")
    
    try:
        while True:
            conn, addr = s.accept()
            # Un hilo nuevo por cada conexión para no bloquear el programa
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\nApagando el servidor y deteniendo motores...")
        motor.set_motor_model(0, 0, 0, 0)