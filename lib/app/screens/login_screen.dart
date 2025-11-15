import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import 'home_screen.dart';

class LoginScreen extends StatefulWidget {
  final VoidCallback? onLogin;
  const LoginScreen({Key? key, this.onLogin}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  String? _errorText;
  bool _loading = false;

  Future<List<Map<String, String>>> _loadTeachers() async {
    final csv = await rootBundle.loadString('assets/data/teachers.csv');
    final lines = LineSplitter.split(csv).toList();
    final headers = lines.first.split(',');
    return lines.skip(1).map((line) {
      final values = line.split(',');
      return Map<String, String>.fromIterables(headers, values);
    }).toList();
  }

  Future<void> _handleLogin() async {
    setState(() {
      _loading = true;
      _errorText = null;
    });
    final teachers = await _loadTeachers();
    final email = _emailController.text.trim();
    final password = _passwordController.text;
    final teacher = teachers.firstWhere(
      (t) => t['email'] == email && t['password'] == password,
      orElse: () => {},
    );
    setState(() {
      _loading = false;
    });
    if (teacher.isNotEmpty) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => HomeScreen(teacherName: teacher['name'] ?? 'Teacher'),
        ),
      );
      widget.onLogin?.call();
    } else {
      setState(() {
        _errorText = 'Invalid email or password';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Teacher Login')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(
                labelText: 'Email',
                prefixIcon: Icon(Icons.email),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Password',
                prefixIcon: Icon(Icons.lock),
              ),
            ),
            if (_errorText != null) ...[
              const SizedBox(height: 12),
              Text(_errorText!, style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loading ? null : _handleLogin,
              child: _loading
                  ? const CircularProgressIndicator()
                  : const Text('Login'),
            ),
            TextButton(
              onPressed: () {},
              child: const Text('Forgot password?'),
            ),
          ],
        ),
      ),
    );
  }
}
