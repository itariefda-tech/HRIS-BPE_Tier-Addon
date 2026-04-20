import 'dart:convert';

import 'package:http/http.dart' as http;

import 'app_config.dart';

class ApiException implements Exception {
  ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class ApiClient {
  Future<dynamic> get(String path, {String? token}) async {
    final response = await _send(
      method: 'GET',
      path: path,
      token: token,
    );
    return response['data'];
  }

  Future<dynamic> post(
    String path, {
    String? token,
    Map<String, dynamic>? body,
  }) async {
    final response = await _send(
      method: 'POST',
      path: path,
      token: token,
      body: body,
    );
    return response['data'];
  }

  Future<Map<String, dynamic>> _send({
    required String method,
    required String path,
    String? token,
    Map<String, dynamic>? body,
  }) async {
    final headers = <String, String>{
      'Accept': 'application/json',
    };
    if (body != null) {
      headers['Content-Type'] = 'application/json';
    }
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }

    final response = await http.Request(
      method,
      Uri.parse('${AppConfig.apiBaseUrl}$path'),
    )
      ..headers.addAll(headers)
      ..body = body == null ? '' : jsonEncode(body);

    final streamed = await response.send();
    final rawResponse = await http.Response.fromStream(streamed);

    Map<String, dynamic>? payload;
    if (rawResponse.body.isNotEmpty) {
      final decoded = jsonDecode(rawResponse.body);
      if (decoded is Map<String, dynamic>) {
        payload = decoded;
      }
    }

    if (rawResponse.statusCode < 200 || rawResponse.statusCode >= 300) {
      throw ApiException(
        _extractMessage(payload) ??
            'Request gagal dengan status ${rawResponse.statusCode}.',
        statusCode: rawResponse.statusCode,
      );
    }

    if (payload == null || !payload.containsKey('data')) {
      throw ApiException('Response API tidak sesuai kontrak.');
    }

    return payload;
  }

  String? _extractMessage(Map<String, dynamic>? payload) {
    if (payload == null) {
      return null;
    }
    final message = payload['message'];
    if (message is String && message.isNotEmpty) {
      return message;
    }
    final detail = payload['detail'];
    if (detail is String && detail.isNotEmpty) {
      return detail;
    }
    return null;
  }
}

