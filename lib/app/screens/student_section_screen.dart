import 'package:flutter/material.dart';

class StudentSectionScreen extends StatefulWidget {
  const StudentSectionScreen({Key? key}) : super(key: key);

  @override
  State<StudentSectionScreen> createState() => _StudentSectionScreenState();
}

class _StudentSectionScreenState extends State<StudentSectionScreen> {
  String? selectedPaper;
  final TextEditingController _studentNameController = TextEditingController();
  String? answerSheetFileName;

  @override
  Widget build(BuildContext context) {
    // Example papers for dropdown
    final papers = [
      '-- Select Paper --',
      'Mathematics Final Exam 2024',
      'Physics Quiz 2024',
      'finalexam',
      'finale',
      'finals',
      'sayon',
    ];
    return Scaffold(
      appBar: AppBar(
        title: const Text('Student Section - Upload Answer Sheet'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: ListView(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text.rich(
                TextSpan(
                  children: [
                    TextSpan(
                        text: 'For Teachers: ',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    TextSpan(
                        text:
                            "Select the question paper and upload a clear image of the student's answer sheet. The AI will automatically extract roll number, section, and answers from the sheet."),
                  ],
                ),
                style: TextStyle(fontSize: 15),
              ),
            ),
            const SizedBox(height: 24),
            const Text('Select Question Paper:'),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: selectedPaper ?? papers[0],
              items: papers.map((paper) {
                return DropdownMenuItem<String>(
                  value: paper,
                  child: Text(paper),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  selectedPaper = value;
                });
              },
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            const Text('Student Name (Optional):'),
            const SizedBox(height: 8),
            TextField(
              controller: _studentNameController,
              decoration: const InputDecoration(
                hintText: 'e.g., John Doe',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            const Text('Upload Answer Sheet Image:'),
            const SizedBox(height: 8),
            Row(
              children: [
                ElevatedButton.icon(
                  onPressed: () {
                    setState(() {
                      answerSheetFileName = 'answer_sheet.jpg';
                    });
                  },
                  icon: const Icon(Icons.file_upload),
                  label: const Text('Choose File'),
                ),
                const SizedBox(width: 16),
                Text(answerSheetFileName ?? 'No file chosen'),
              ],
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.camera_alt),
              label: const Text('Start Camera'),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                // TODO: Implement upload logic
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                      content: Text('Answer sheet submitted! (Demo)')),
                );
              },
              child: const Text('Submit Answer Sheet'),
              style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(48)),
            ),
          ],
        ),
      ),
    );
  }
}
