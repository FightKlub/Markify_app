import 'package:flutter/material.dart';
import 'screens/splash_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/login_screen.dart';

class MarkifyApp extends StatefulWidget {
  const MarkifyApp({Key? key}) : super(key: key);

  @override
  State<MarkifyApp> createState() => _MarkifyAppState();
}

class _MarkifyAppState extends State<MarkifyApp> {
  bool _showOnboarding = false;
  bool _showLogin = false;

  @override
  void initState() {
    super.initState();
    // Simulate splash delay
    Future.delayed(const Duration(seconds: 2), () {
      setState(() {
        _showOnboarding = true;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Markify',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      debugShowCheckedModeBanner: false,
      home: _buildHome(),
    );
  }

  Widget _buildHome() {
    if (!_showOnboarding) {
      return const SplashScreen();
    } else if (!_showLogin) {
      return OnboardingScreen(
        onGetStarted: () {
          setState(() {
            _showLogin = true;
          });
        },
      );
    } else {
      return LoginScreen(
        onLogin: () {
          // TODO: Navigate to dashboard after login
        },
      );
    }
  }
}
