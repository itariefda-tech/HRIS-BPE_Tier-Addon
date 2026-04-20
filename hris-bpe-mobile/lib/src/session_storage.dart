import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import 'models.dart';

class SessionStorage {
  static const _sessionKey = 'guard_mobile_session';

  Future<AuthSession?> readSession() async {
    final preferences = await SharedPreferences.getInstance();
    final rawValue = preferences.getString(_sessionKey);
    if (rawValue == null || rawValue.isEmpty) {
      return null;
    }

    final decoded = jsonDecode(rawValue);
    if (decoded is! Map<String, dynamic>) {
      return null;
    }
    return AuthSession.fromJson(decoded);
  }

  Future<void> writeSession(AuthSession session) async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setString(_sessionKey, jsonEncode(session.toJson()));
  }

  Future<void> clearSession() async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.remove(_sessionKey);
  }
}

