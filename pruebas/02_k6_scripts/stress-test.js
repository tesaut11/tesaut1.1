import http from 'k6/http';
import { check, sleep } from 'k6';

// Función para generar IPs aleatorias y simular tráfico real distribuido
function randomIP() {
    return `${Math.floor(Math.random() * 255) + 1}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
}

export const options = {
    stages: [
        { duration: '60s', target: 50 },   // Rampa de subida (fase de calentamiento)
        { duration: '60s', target: 50 },   // Carga nominal (operación estable)
        { duration: '120s', target: 150 }, // Pico estocástico (activa el HPA o el Throttling)
        { duration: '120s', target: 10 },  // Rampa de bajada (recuperación)
    ],
};

export default function () {
    // Reemplaza esto con la IP o dominio local de tu Ingress
    const url = 'http://localhost';

    // Inyectamos la IP falsa en las cabeceras
    const params = {
        headers: {
            'X-Forwarded-For': randomIP(),
            'User-Agent': 'k6-load-tester',
        },
    };

    const res = http.get(url, params);

    check(res, {
        'status is 200': (r) => r.status === 200,
    });

    // Pausa corta para simular comportamiento humano y no saturar los puertos locales
    sleep(1);
}