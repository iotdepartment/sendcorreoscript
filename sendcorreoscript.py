import paho.mqtt.client as mqtt 
import json 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
import time 


# -----------------------------
# EXTRAE LA INFO DEL MQTT
# -----------------------------
mqtt_BROKER = "10.195.250.100" 
mqtt_PORT = 1883 
mqtt_TOPIC = ["Sensors/DESTINATARIOS", "Sensors/CUERPO"]
# -----------------------------
# FUNCION PARA ENVIAR CORREO 
# -----------------------------
def enviar_correo(destinatario, mensaje_texto):
    
    correo_origen = "Hector.Castillo@toyodagosei.com" 

    mensaje = MIMEMultipart() 
    mensaje["From"] = correo_origen 
    mensaje["To"] = destinatario 
    mensaje["Subject"] = "SE AH DETECTADO UN SENSOR OFFLINE"
    mensaje.attach(MIMEText(mensaje_texto, "plain"))

    try: 
        servidor = smtplib.SMTP("kysmtp.tggroup.local", 25) 
        servidor.ehlo()  # Identificarse con el servidor SMTP
        servidor.sendmail(correo_origen, destinatario, mensaje.as_string()) # Enviar el correo
        servidor.quit() # Cerrar la conexión con el servidor SMTP
        print("Correo enviado") 
    except Exception as e: 
        print("Error enviando correo:", e)

# -----------------------------
# CALLBACK MQTT
# ----------------------------
def on_connect(client, userdata, flags, rc): 
    print("Conectado con codigo:", rc) 
    client.subscribe("Sensors/CUERPO") # Recibe el contenido del mensaje
    client.subscribe("Sensors/DESTINATARIOS") # Recibe el contenido del destinatario
    r, _ = client.subscribe("Sensors/DESTINATARIOS")
    print("Sub DESTINATARIO:", r)
    r, _ = client.subscribe("Sensors/CUERPO")
    print("Sub CUERPO:", r)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Suscripcion confirmada. mid:", mid, "qos:", granted_qos)
    client.on_subscribe = on_subscribe
def on_message(client, userdata, msg):
    print("Mensaje recibido:", msg.topic, msg.payload.decode()) # Imprime el contenido del mensaje recibido
    if msg.topic == "Sensors/CUERPO": # Imprime el contenido del mensaje recibido
        userdata['CUERPO'] = msg.payload.decode() # Almacena el mensaje en userdata
   
    elif msg.topic == "Sensors/DESTINATARIOS": # Imprime el contenido del destinatario recibido
        userdata['DESTINATARIO'] = msg.payload.decode() # Almacena el destinatario en userdata

        if 'CUERPO' in userdata and 'DESTINATARIO' in userdata: # Verifica si almacena ambos datos
            print("Enviando correo a:", userdata['DESTINATARIO']) # Llama a la función para enviar el correo
      
            enviar_correo(userdata['DESTINATARIO'], userdata['CUERPO']) # Envia el correo
            
        # Limpiar los datos después de enviar el correo
            userdata.clear()


# -----------------------------
# INICIO MQTT
# -----------------------------
client = mqtt.Client() 

#Asignar callbacks
client = mqtt.Client(userdata={})
client.on_connect = on_connect # Funcion de conexion
client.on_message = on_message # Funcion de mensaje recibido

# -----------------------------
# REINTENTAR CONEXION MQTT EN CASO DE FALLO
# -----------------------------

# Intentar conectar al broker MQTT hasta que tenga éxito
while True:
    try:
        print("Intentando conectar al broker MQTT...")
        client.connect(mqtt_BROKER, mqtt_PORT, 60)
        print("Conectado exitosamente al broker MQTT")
        break # Salir del bucle si la conexión es exitosa
    
    except Exception as e:
        print("Error de conexion:", e)
        print("Reintentando en 30 segundos...")
        time.sleep(30)
    
client.loop_forever() # Mantener el bucle de red para procesar mensajes entrantes
