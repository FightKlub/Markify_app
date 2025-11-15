import 'package:flutter/material.dart';

class OnboardingScreen extends StatelessWidget {
  final VoidCallback onGetStarted;
  const OnboardingScreen({Key? key, required this.onGetStarted})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PageView(
        children: [
          _buildPage('Upload answer sheets easily.', Icons.upload_file),
          _buildPage('Create & manage answer keys.', Icons.edit_document),
          _buildPage('Instant evaluation & results.', Icons.analytics),
        ],
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(24.0),
        child: ElevatedButton(
          onPressed: onGetStarted,
          child: const Text('Get Started'),
        ),
      ),
    );
  }

  Widget _buildPage(String text, IconData icon) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 100, color: Colors.blue),
          const SizedBox(height: 32),
          Text(
            text,
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
