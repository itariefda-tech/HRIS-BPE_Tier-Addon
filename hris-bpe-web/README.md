# HRIS BPE Web

Web admin untuk `PHASE 11.5 UI-1 BASIC` dengan stack:

- Next.js App Router
- Tailwind CSS
- TanStack Query
- Zustand
- React Hook Form

## Scope

Iterasi awal fokus pada:

- login + session basic
- dashboard basic
- employee
- client + contract
- site + post
- deployment
- schedule
- attendance

## Menjalankan

1. Pastikan backend FastAPI berjalan di `http://127.0.0.1:8000`
2. Salin `.env.example` menjadi `.env.local`
3. Jalankan:

```bash
npm install
npm run dev
```

Default URL frontend:

```text
http://127.0.0.1:3000
```

Default URL API:

```text
http://127.0.0.1:8000/api/v1
```

## Akun Seed Demo

- `owner@bpe.co.id / Admin123!`
- `supervisor@bpe.co.id / Supervisor123!`
- `guard@bpe.co.id / Guard123!`

## Catatan Gap

- endpoint mobile `/my/schedules` belum ada di backend saat scaffold ini dibuat
- beberapa modul Basic masih belum punya endpoint `detail` dan `update`
- filter list saat ini disiapkan client-side dulu untuk validasi flow
