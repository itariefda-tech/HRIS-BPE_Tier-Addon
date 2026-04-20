import 'api_client.dart';
import 'models.dart';

class AuthRepository {
  final ApiClient _apiClient = ApiClient();

  Future<AuthSession> login({
    required String identifier,
    required String password,
  }) async {
    final payload = await _apiClient.post(
      '/auth/login',
      body: {
        'identifier': identifier,
        'password': password,
      },
    );
    return AuthSession.fromJson(payload as Map<String, dynamic>);
  }
}

