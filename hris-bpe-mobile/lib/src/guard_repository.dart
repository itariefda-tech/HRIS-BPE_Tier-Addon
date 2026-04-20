import 'api_client.dart';
import 'models.dart';

class GuardRepository {
  final ApiClient _apiClient = ApiClient();

  Future<List<MyWorkSchedule>> listMySchedules(String token) async {
    final payload = await _apiClient.get('/my/schedules', token: token);
    final items = payload as List<dynamic>;
    return items
        .map((item) => MyWorkSchedule.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<AttendanceRecord>> listAttendanceRecords(String token) async {
    final payload = await _apiClient.get('/attendance/records', token: token);
    final items = payload as List<dynamic>;
    return items
        .map((item) => AttendanceRecord.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<AttendanceRecord> checkIn({
    required String token,
    required int workScheduleId,
    required double latitude,
    required double longitude,
  }) async {
    final payload = await _apiClient.post(
      '/attendance/check-in',
      token: token,
      body: {
        'work_schedule_id': workScheduleId,
        'latitude': latitude.toStringAsFixed(6),
        'longitude': longitude.toStringAsFixed(6),
        'method': 'gps',
      },
    );
    return AttendanceRecord.fromJson(payload as Map<String, dynamic>);
  }

  Future<AttendanceRecord> checkOut({
    required String token,
    required int workScheduleId,
    required double latitude,
    required double longitude,
  }) async {
    final payload = await _apiClient.post(
      '/attendance/check-out',
      token: token,
      body: {
        'work_schedule_id': workScheduleId,
        'latitude': latitude.toStringAsFixed(6),
        'longitude': longitude.toStringAsFixed(6),
        'method': 'gps',
      },
    );
    return AttendanceRecord.fromJson(payload as Map<String, dynamic>);
  }
}

