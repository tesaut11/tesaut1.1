import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '60s', target: 10 },   // 0 a 60s: Calentamiento
    { duration: '60s', target: 10 },   // 60 a 120s: Línea base
    { duration: '15s', target: 300 },  // 120 a 135s: Inyección de estrés (suavizada para el HPA)
    { duration: '105s', target: 300 }, // 135 a 240s: Pico masivo sostenido
    { duration: '10s', target: 0 },    // 240 a 250s: Rampa de bajada rápida
    { duration: '110s', target: 0 },   // 250 a 360s: Observación
  ],
  thresholds: {
    http_req_duration: ['p(95)<170'],
  },
};

export default function () {
  // AUMENTO VITAL: Obligamos a K6 a esperar hasta 120s para que no marque error 
  // mientras el HPA sufre su "arranque en frío" (cold start).
  const res = http.get('http://localhost:8080/', { timeout: '120s' }); // Mantén el timeout
  
  check(res, {
    'status es 200 (OK)': (r) => r.status === 200,
    'status es 429 (Throttled)': (r) => r.status === 429,
  });
  
  sleep(1);
}