import 'package:flutter/material.dart';
import 'teacher_section_screen.dart';
import 'student_section_screen.dart';
import 'results_section_screen.dart';

class HomeScreen extends StatelessWidget {
  final String teacherName;
  const HomeScreen({Key? key, required this.teacherName}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Markify Dashboard'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: CircleAvatar(
              child: Text(teacherName[0]),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Welcome, $teacherName!',
                  style: const TextStyle(
                      fontSize: 22, fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              // Teacher Section
              _SectionCard(
                title: 'Teacher Section',
                icon: Icons.school,
                color: Colors.blue,
                children: [
                  _SectionButton(
                    icon: Icons.document_scanner,
                    label: 'OCR Upload',
                    onTap: () {
                      Navigator.of(context).push(MaterialPageRoute(
                        builder: (_) => TeacherSectionScreen(),
                      ));
                    },
                  ),
                ],
              ),
              const SizedBox(height: 24),
              // Student Section
              _SectionCard(
                title: 'Student Section',
                icon: Icons.people,
                color: Colors.green,
                children: [
                  _SectionButton(
                    icon: Icons.upload_file,
                    label: 'Upload Answer Sheet',
                    onTap: () {
                      Navigator.of(context).push(MaterialPageRoute(
                        builder: (_) => StudentSectionScreen(),
                      ));
                    },
                  ),
                ],
              ),
              const SizedBox(height: 24),
              // Results Section
              _SectionCard(
                title: 'Results Section',
                icon: Icons.bar_chart,
                color: Colors.purple,
                children: [
                  _SectionButton(
                    icon: Icons.bar_chart,
                    label: 'Results',
                    onTap: () {
                      Navigator.of(context).push(MaterialPageRoute(
                        builder: (_) => ResultsSectionScreen(),
                      ));
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color color;
  final List<Widget> children;
  const _SectionCard(
      {required this.title,
      required this.icon,
      required this.color,
      required this.children});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: color.withOpacity(0.15),
                  child: Icon(icon, color: color, size: 28),
                ),
                const SizedBox(width: 12),
                Text(title,
                    style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: color)),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 16,
              runSpacing: 16,
              children: children,
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  const _SectionButton(
      {required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 140,
      height: 48,
      child: ElevatedButton.icon(
        style: ElevatedButton.styleFrom(
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          backgroundColor: Theme.of(context).colorScheme.surface,
          foregroundColor: Theme.of(context).colorScheme.primary,
          elevation: 1,
        ),
        icon: Icon(icon, size: 22),
        label: Text(label, style: const TextStyle(fontSize: 15)),
        onPressed: onTap,
      ),
    );
  }
}

class _PlaceholderScreen extends StatelessWidget {
  final String title;
  const _PlaceholderScreen({required this.title});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Center(
        child: Text('$title screen coming soon!',
            style: const TextStyle(fontSize: 20)),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;
  const _StatCard(
      {required this.title,
      required this.value,
      required this.icon,
      required this.color});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: color.withOpacity(0.1),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(value,
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.black)),
            const SizedBox(height: 4),
            Text(title, style: const TextStyle(fontSize: 12)),
          ],
        ),
      ),
    );
  }
}

class _ActivityTile extends StatelessWidget {
  final String text;
  const _ActivityTile({required this.text});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const Icon(Icons.history, color: Colors.blue),
      title: Text(text),
    );
  }
}

class _HomeOption extends StatelessWidget {
  final IconData icon;
  final String label;
  const _HomeOption({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 2,
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () {},
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 36, color: Colors.blue),
              const SizedBox(height: 8),
              Text(label,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 14)),
            ],
          ),
        ),
      ),
    );
  }
}
