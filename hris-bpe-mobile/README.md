# HRIS BPE Mobile

Flutter app minimal untuk guard pada phase `PHASE 11.5 UI BASIC`.

## Scope saat ini

- login guard
- lihat `my schedules`
- lihat status hadir hari ini
- check-in
- check-out

## Catatan environment

Folder ini dibuat manual karena tool `flutter` belum tersedia di environment kerja saat implementasi.

Jika platform folder (`android`, `ios`, `web`, `windows`, dst.) belum ada, jalankan dari folder ini:

```powershell
flutter create --platforms=android .
flutter pub get
```

Setelah folder platform dibuat, tambahkan permission lokasi sesuai target platform sebelum mencoba check-in dan check-out.

SDK Android minimum yang sudah dipakai di environment kerja ini:

- `C:\Android\Sdk\platform-tools`
- `C:\Android\Sdk\cmdline-tools\latest`
- `platforms;android-35`
- `build-tools;35.0.0`

Helper script untuk Android device fisik tersedia di:

```powershell
.\scripts\run-android-device.ps1 -FlutterSdkPath C:\path\to\flutter
```

## Jalankan

Default base URL:

```text
http://127.0.0.1:8000/api/v1
```

Untuk Android emulator, override agar mengarah ke host Windows:

```powershell
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

Untuk device fisik, gunakan IP LAN backend:

```powershell
flutter run --dart-define=API_BASE_URL=http://<IP-LAN>:8000/api/v1
```

Backend juga harus listen ke LAN, bukan hanya `127.0.0.1`. Jalankan dari root repo:

```powershell
.\scripts\run-backend-lan.ps1
```

Contoh IP LAN yang terdeteksi di environment ini:

```text
192.168.1.111
```

## Endpoint yang dipakai

- `POST /api/v1/auth/login`
- `GET /api/v1/my/schedules`
- `GET /api/v1/attendance/records`
- `POST /api/v1/attendance/check-in`
- `POST /api/v1/attendance/check-out`

## Seed guard

- `guard@bpe.co.id`
- `Guard123!`
