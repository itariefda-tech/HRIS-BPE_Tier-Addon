import 'package:flutter/material.dart';

import 'app_controller.dart';
import 'auth_repository.dart';
import 'guard_home_page.dart';
import 'guard_repository.dart';
import 'login_page.dart';
import 'session_storage.dart';

class GuardMobileApp extends StatefulWidget {
  const GuardMobileApp({super.key});

  @override
  State<GuardMobileApp> createState() => _GuardMobileAppState();
}

class _GuardMobileAppState extends State<GuardMobileApp> {
  late final AppController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AppController(
      authRepository: AuthRepository(),
      guardRepository: GuardRepository(),
      sessionStorage: SessionStorage(),
    );
    _controller.restoreSession();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'HRIS BPE Mobile',
          theme: ThemeData(
            colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2F6F43)),
            scaffoldBackgroundColor: const Color(0xFFF3F5F1),
            useMaterial3: true,
          ),
          home: _buildHome(),
        );
      },
    );
  }

  Widget _buildHome() {
    if (_controller.isBootstrapping) {
      return const _SplashPage();
    }

    if (_controller.session == null) {
      return LoginPage(controller: _controller);
    }

    return GuardHomePage(controller: _controller);
  }
}

class _SplashPage extends StatelessWidget {
  const _SplashPage();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}

