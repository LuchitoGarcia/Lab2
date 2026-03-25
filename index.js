const net = require('net');

// La IP de tu Raspberry Pi y el puerto del servidor [cite: 694, 722]
const SERVER_IP = '100.70.111.11'; 
const PORT = 65432; 

function sendCmd(command) {
    const client = new net.Socket();

    // Intentamos conectar con el coche [cite: 732]
    client.connect(PORT, SERVER_IP, () => {
        console.log('Enviando: ' + command);
        client.write(command); // Mandamos la orden al coche [cite: 742]
    });

    // Cuando el coche nos responde con datos [cite: 745]
    client.on('data', (data) => {
        console.log('Recibido: ' + data);
        
        if (command === 'stats') {
    try {
        const stats = JSON.parse(data.toString());
        document.getElementById('dist').innerText = stats.distance_cm;
        document.getElementById('bat').innerText = stats.battery_voltage;
        document.getElementById('temp').innerText = stats.cpu_temp;
        document.getElementById('status').innerText = "Conectado";
    } catch (e) {
        console.error("Error leyendo JSON:", e);
    }
}
        client.destroy(); // Cerramos la conexión tras recibir respuesta [cite: 751]
    });

    client.on('error', (err) => {
        document.getElementById('status').innerText = "Error: No se encuentra el coche";
        console.error(err);
        client.destroy();
    });
}