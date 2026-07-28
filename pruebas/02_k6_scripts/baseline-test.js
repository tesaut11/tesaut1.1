import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    vus: 10,
    duration: '30s',
    thresholds: {
        http_req_duration: ['p(95)<500'], // Fallará si p95 es mayor a 500ms
    },
};

export default function () {
    http.get('http://localhost');
    sleep(1);
}