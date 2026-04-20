import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';

import 'api_client.dart';
import 'auth_repository.dart';
import 'guard_repository.dart';
import 'models.dart';
import 'session_storage.dart';

class AppController extends ChangeNotifier {
  AppController({
    required this.authRepository,
    required this.guardRepository,
    required this.sessionStorage,
  });

  final AuthRepository authRepository;
  final GuardRepository guardRepository;
  final SessionStorage sessionStorage;

  AuthSession? _session;
  bool _isBootstrapping = true;
  bool _isSubmittingLogin = false;
  bool _isRefreshing = false;
  bool _isSubmittingAttendance = false;
  String? _errorMessage;
  String? _infoMessage;
  List<MyWorkSchedule> _schedules = const [];
  List<AttendanceRecord> _attendanceRecords = const [];
  int? _selectedScheduleId;

  AuthSession? get session => _session;
  bool get isBootstrapping => _isBootstrapping;
  bool get isSubmittingLogin => _isSubmittingLogin;
  bool get isRefreshing => _isRefreshing;
  bool get isSubmittingAttendance => _isSubmittingAttendance;
  String? get errorMessage => _errorMessage;
  String? get infoMessage => _infoMessage;
  List<MyWorkSchedule> get schedules => _schedules;
  List<AttendanceRecord> get attendanceRecords => _attendanceRecords;

  MyWorkSchedule? get selectedSchedule {
    if (_selectedScheduleId == null) {
      return null;
    }

    for (final schedule in _schedules) {
      if (schedule.id == _selectedScheduleId) {
        return schedule;
      }
    }
    return null;
  }

  AttendanceRecord? get selectedAttendanceRecord {
    final schedule = selectedSchedule;
    if (schedule == null) {
      return null;
    }
    for (final record in _attendanceRecords) {
      if (record.workScheduleId == schedule.id) {
        return record;
      }
    }
    return null;
  }

  List<MyWorkSchedule> get todaySchedules {
    final today = _todayIso();
    return _schedules.where((item) => item.scheduledDate == today).toList();
  }

  String get todayAttendanceStatus {
    final schedule = _preferredTodaySchedule();
    if (schedule == null) {
      return 'Tidak ada schedule hari ini';
    }

    final record = _attendanceForSchedule(schedule.id);
    if (record == null) {
      return 'Belum check-in';
    }
    if (record.checkOutDateTime != null) {
      return 'Sudah check-out';
    }
    if (record.minutesLate > 0) {
      return 'Sudah check-in (late)';
    }
    return 'Sudah check-in';
  }

  bool get canCheckIn {
    final schedule = selectedSchedule ?? _preferredTodaySchedule();
    if (schedule == null) {
      return false;
    }
    final record = _attendanceForSchedule(schedule.id);
    return record == null;
  }

  bool get canCheckOut {
    final schedule = selectedSchedule ?? _preferredTodaySchedule();
    if (schedule == null) {
      return false;
    }
    final record = _attendanceForSchedule(schedule.id);
    return record != null && record.checkOutDateTime == null;
  }

  Future<void> restoreSession() async {
    try {
      _session = await sessionStorage.readSession();
      if (_session != null) {
        await refreshData(silent: true);
      }
    } catch (error) {
      _errorMessage = _toMessage(error);
    } finally {
      _isBootstrapping = false;
      notifyListeners();
    }
  }

  Future<void> login({
    required String identifier,
    required String password,
  }) async {
    _clearMessages();
    _isSubmittingLogin = true;
    notifyListeners();

    try {
      final session = await authRepository.login(
        identifier: identifier,
        password: password,
      );
      _session = session;
      await sessionStorage.writeSession(session);
      await refreshData(silent: true);
      _infoMessage = 'Login berhasil.';
    } catch (error) {
      _errorMessage = _toMessage(error);
    } finally {
      _isSubmittingLogin = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    _session = null;
    _schedules = const [];
    _attendanceRecords = const [];
    _selectedScheduleId = null;
    _clearMessages();
    await sessionStorage.clearSession();
    notifyListeners();
  }

  Future<void> refreshData({bool silent = false}) async {
    if (_session == null) {
      return;
    }

    if (!silent) {
      _clearMessages();
      _isRefreshing = true;
      notifyListeners();
    }

    try {
      final token = _session!.accessToken;
      final schedules = await guardRepository.listMySchedules(token);
      final attendanceRecords = await guardRepository.listAttendanceRecords(token);
      schedules.sort(_compareSchedules);
      _schedules = schedules;
      _attendanceRecords = attendanceRecords;
      _syncSelectedSchedule();
      if (!silent) {
        _infoMessage = 'Data guard berhasil diperbarui.';
      }
    } catch (error) {
      _errorMessage = _toMessage(error);
    } finally {
      if (!silent) {
        _isRefreshing = false;
      }
      notifyListeners();
    }
  }

  void selectSchedule(int scheduleId) {
    _selectedScheduleId = scheduleId;
    _clearMessages();
    notifyListeners();
  }

  Future<void> checkIn() async {
    final schedule = selectedSchedule ?? _preferredTodaySchedule();
    if (schedule == null || _session == null) {
      return;
    }

    await _submitAttendanceAction(
      successMessage: 'Check-in berhasil dicatat.',
      action: (position) => guardRepository.checkIn(
        token: _session!.accessToken,
        workScheduleId: schedule.id,
        latitude: position.latitude,
        longitude: position.longitude,
      ),
    );
  }

  Future<void> checkOut() async {
    final schedule = selectedSchedule ?? _preferredTodaySchedule();
    if (schedule == null || _session == null) {
      return;
    }

    await _submitAttendanceAction(
      successMessage: 'Check-out berhasil dicatat.',
      action: (position) => guardRepository.checkOut(
        token: _session!.accessToken,
        workScheduleId: schedule.id,
        latitude: position.latitude,
        longitude: position.longitude,
      ),
    );
  }

  Future<void> _submitAttendanceAction({
    required String successMessage,
    required Future<AttendanceRecord> Function(Position position) action,
  }) async {
    _clearMessages();
    _isSubmittingAttendance = true;
    notifyListeners();

    try {
      final position = await _resolvePosition();
      await action(position);
      await refreshData(silent: true);
      _infoMessage = successMessage;
    } catch (error) {
      _errorMessage = _toMessage(error);
    } finally {
      _isSubmittingAttendance = false;
      notifyListeners();
    }
  }

  Future<Position> _resolvePosition() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('Location service belum aktif di device.');
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }

    if (permission == LocationPermission.denied) {
      throw Exception('Izin lokasi ditolak.');
    }

    if (permission == LocationPermission.deniedForever) {
      throw Exception('Izin lokasi ditolak permanen.');
    }

    return Geolocator.getCurrentPosition();
  }

  AttendanceRecord? _attendanceForSchedule(int scheduleId) {
    for (final record in _attendanceRecords) {
      if (record.workScheduleId == scheduleId) {
        return record;
      }
    }
    return null;
  }

  MyWorkSchedule? _preferredTodaySchedule() {
    final today = todaySchedules;
    if (today.isEmpty) {
      return selectedSchedule;
    }

    final selected = selectedSchedule;
    if (selected != null && selected.scheduledDate == _todayIso()) {
      return selected;
    }
    return today.first;
  }

  void _syncSelectedSchedule() {
    if (_schedules.isEmpty) {
      _selectedScheduleId = null;
      return;
    }

    if (_selectedScheduleId != null) {
      for (final schedule in _schedules) {
        if (schedule.id == _selectedScheduleId) {
          return;
        }
      }
    }

    final preferred = _preferredScheduleSelection();
    _selectedScheduleId = preferred?.id;
  }

  MyWorkSchedule? _preferredScheduleSelection() {
    final today = _todayIso();
    for (final schedule in _schedules) {
      if (schedule.scheduledDate == today) {
        return schedule;
      }
    }
    return _schedules.firstOrNull;
  }

  int _compareSchedules(MyWorkSchedule left, MyWorkSchedule right) {
    final leftToday = left.scheduledDate == _todayIso();
    final rightToday = right.scheduledDate == _todayIso();
    if (leftToday != rightToday) {
      return leftToday ? -1 : 1;
    }
    return right.scheduledStartDateTime.compareTo(left.scheduledStartDateTime);
  }

  String _todayIso() {
    final now = DateTime.now();
    final month = now.month.toString().padLeft(2, '0');
    final day = now.day.toString().padLeft(2, '0');
    return '${now.year}-$month-$day';
  }

  void _clearMessages() {
    _errorMessage = null;
    _infoMessage = null;
  }

  String _toMessage(Object error) {
    if (error is ApiException) {
      return error.message;
    }
    return error.toString().replaceFirst('Exception: ', '');
  }
}

extension _FirstOrNullExtension<T> on List<T> {
  T? get firstOrNull => isEmpty ? null : first;
}
