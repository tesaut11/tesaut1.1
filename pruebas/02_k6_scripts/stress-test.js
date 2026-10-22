import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  stages: [
    { duration: '60s', target: 10 },  // Fase 1: Rampa de subida
    { duration: '60s', target: 10 },  // Fase 2: Carga nominal (Línea base)
    { duration: '120s', target: 300 }, // Fase 3: Pico de estrés masivo
    { duration: '120s', target: 0 },  // Fase 4: Descenso y recuperación
  ],
  thresholds: {
    http_req_duration: ['p(95)<170'], // SLA de degradación (170 ms)
  },
};

export default function () {
  const url = 'http://localhost:8080/';
  const params = {
    headers: {
      // Emulación de tráfico distribuido con IPs aleatorias
      'X-Forwarded-For': `192.168.1.${Math.floor(Math.random() * 255)}`,
    },
  };
  http.get(url, params);
  sleep(1);
}