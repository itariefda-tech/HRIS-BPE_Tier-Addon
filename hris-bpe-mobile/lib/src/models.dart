class AuthUser {
  AuthUser({
    required this.id,
    required this.employeeId,
    required this.username,
    required this.email,
    required this.permissionCodes,
  });

  final int id;
  final int? employeeId;
  final String username;
  final String email;
  final List<String> permissionCodes;

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    return AuthUser(
      id: json['id'] as int,
      employeeId: json['employee_id'] as int?,
      username: json['username'] as String? ?? '',
      email: json['email'] as String? ?? '',
      permissionCodes: (json['permission_codes'] as List<dynamic>? ?? const [])
          .map((item) => item.toString())
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'employee_id': employeeId,
      'username': username,
      'email': email,
      'permission_codes': permissionCodes,
    };
  }
}

class AuthSession {
  AuthSession({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.sessionId,
    required this.accessTokenExpiresAt,
    required this.refreshTokenExpiresAt,
    required this.user,
  });

  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final String sessionId;
  final String accessTokenExpiresAt;
  final String refreshTokenExpiresAt;
  final AuthUser user;

  factory AuthSession.fromJson(Map<String, dynamic> json) {
    return AuthSession(
      accessToken: json['access_token'] as String? ?? '',
      refreshToken: json['refresh_token'] as String? ?? '',
      tokenType: json['token_type'] as String? ?? 'bearer',
      sessionId: json['session_id'] as String? ?? '',
      accessTokenExpiresAt: json['access_token_expires_at'] as String? ?? '',
      refreshTokenExpiresAt: json['refresh_token_expires_at'] as String? ?? '',
      user: AuthUser.fromJson(json['user'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'token_type': tokenType,
      'session_id': sessionId,
      'access_token_expires_at': accessTokenExpiresAt,
      'refresh_token_expires_at': refreshTokenExpiresAt,
      'user': user.toJson(),
    };
  }
}

class MyWorkSchedule {
  MyWorkSchedule({
    required this.id,
    required this.employeeId,
    required this.employeeDeploymentId,
    required this.clientSiteId,
    required this.sitePostId,
    required this.shiftTypeId,
    required this.scheduledDate,
    required this.scheduledStartDateTime,
    required this.scheduledEndDateTime,
    required this.scheduleStatus,
    required this.clientSiteName,
    required this.sitePostName,
    required this.shiftTypeName,
  });

  final int id;
  final int employeeId;
  final int employeeDeploymentId;
  final int clientSiteId;
  final int? sitePostId;
  final int shiftTypeId;
  final String scheduledDate;
  final String scheduledStartDateTime;
  final String scheduledEndDateTime;
  final String scheduleStatus;
  final String? clientSiteName;
  final String? sitePostName;
  final String? shiftTypeName;

  factory MyWorkSchedule.fromJson(Map<String, dynamic> json) {
    return MyWorkSchedule(
      id: json['id'] as int,
      employeeId: json['employee_id'] as int,
      employeeDeploymentId: json['employee_deployment_id'] as int,
      clientSiteId: json['client_site_id'] as int,
      sitePostId: json['site_post_id'] as int?,
      shiftTypeId: json['shift_type_id'] as int,
      scheduledDate: json['scheduled_date'] as String? ?? '',
      scheduledStartDateTime: json['scheduled_start_datetime'] as String? ?? '',
      scheduledEndDateTime: json['scheduled_end_datetime'] as String? ?? '',
      scheduleStatus: json['schedule_status'] as String? ?? '',
      clientSiteName: json['client_site_name'] as String?,
      sitePostName: json['site_post_name'] as String?,
      shiftTypeName: json['shift_type_name'] as String?,
    );
  }
}

class AttendanceRecord {
  AttendanceRecord({
    required this.id,
    required this.workScheduleId,
    required this.attendanceDate,
    required this.attendanceStatus,
    required this.minutesLate,
    required this.checkInDateTime,
    required this.checkOutDateTime,
  });

  final int id;
  final int workScheduleId;
  final String attendanceDate;
  final String attendanceStatus;
  final int minutesLate;
  final String? checkInDateTime;
  final String? checkOutDateTime;

  factory AttendanceRecord.fromJson(Map<String, dynamic> json) {
    return AttendanceRecord(
      id: json['id'] as int,
      workScheduleId: json['work_schedule_id'] as int,
      attendanceDate: json['attendance_date'] as String? ?? '',
      attendanceStatus: json['attendance_status'] as String? ?? '',
      minutesLate: json['minutes_late'] as int? ?? 0,
      checkInDateTime: json['check_in_datetime'] as String?,
      checkOutDateTime: json['check_out_datetime'] as String?,
    );
  }
}

