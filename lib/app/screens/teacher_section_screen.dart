import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import '../../config.dart';

class TeacherSectionScreen extends StatefulWidget {
  const TeacherSectionScreen({Key? key}) : super(key: key);
  @override
  State<TeacherSectionScreen> createState() => _TeacherSectionScreenState();
}

class _TeacherSectionScreenState extends State<TeacherSectionScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Teacher Section - Upload Answer Key'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'OCR Upload'),
            Tab(text: 'Manual Input'),
            Tab(text: 'Manage Papers'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          _OcrUploadTab(),
          _ManualInputTab(),
          _ManagePapersTab(),
        ],
      ),
    );
  }
}

// OCR Upload Tab
class _OcrUploadTab extends StatefulWidget {
  const _OcrUploadTab();
  @override
  State<_OcrUploadTab> createState() => _OcrUploadTabState();
}

class _OcrUploadTabState extends State<_OcrUploadTab> {
  final TextEditingController _paperNameController = TextEditingController();
  File? _selectedImage;
  bool _loading = false;
  String? _resultMessage;

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);
    if (picked != null) {
      setState(() {
        _selectedImage = File(picked.path);
      });
    }
  }

  Future<void> _pickCamera() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.camera);
    if (picked != null) {
      setState(() {
        _selectedImage = File(picked.path);
      });
    }
  }

  Future<void> _upload() async {
    final paperName = _paperNameController.text.trim();
    if (paperName.isEmpty) {
      setState(() {
        _resultMessage = 'Please enter the question paper name.';
      });
      return;
    }
    if (_selectedImage == null) {
      setState(() {
        _resultMessage = 'Please select an image.';
      });
      return;
    }
    setState(() {
      _loading = true;
      _resultMessage = null;
    });
    try {
      var uri = Uri.parse('${Config.apiBaseUrl}/api/answer-key-ocr');
      var request = http.MultipartRequest('POST', uri)
        ..fields['paper_name'] = paperName
        ..files.add(
            await http.MultipartFile.fromPath('image', _selectedImage!.path));
      var response = await request.send();
      var respStr = await response.stream.bytesToString();
      if (response.statusCode == 200) {
        setState(() {
          _resultMessage = 'Success: Answer key uploaded!';
        });
      } else {
        setState(() {
          _resultMessage = 'Error: ' + respStr;
        });
      }
    } catch (e) {
      setState(() {
        _resultMessage = 'Error: $e';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: ListView(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blue[50],
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Text(
              'OCR Upload: Upload an image of your answer key and let AI extract the correct answers automatically. Supports JPG, PNG, and other common image formats.',
              style: TextStyle(fontSize: 15),
            ),
          ),
          const SizedBox(height: 24),
          TextField(
            controller: _paperNameController,
            decoration: const InputDecoration(
              labelText: 'Question Paper Name',
              hintText: 'e.g., Mathematics Final Exam 2024',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          const Text('Upload Answer Key Image:'),
          const SizedBox(height: 8),
          Row(
            children: [
              ElevatedButton.icon(
                onPressed: _pickImage,
                icon: const Icon(Icons.file_upload),
                label: const Text('Choose File'),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(_selectedImage != null
                    ? _selectedImage!.path.split(Platform.pathSeparator).last
                    : 'No file chosen'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text('Or use your camera:'),
          const SizedBox(height: 8),
          ElevatedButton.icon(
            onPressed: _pickCamera,
            icon: const Icon(Icons.camera_alt),
            label: const Text('Start Camera'),
          ),
          const SizedBox(height: 24),
          _loading
              ? const Center(child: CircularProgressIndicator())
              : ElevatedButton(
                  onPressed: _upload,
                  child: const Text('Upload Answer Key'),
                  style: ElevatedButton.styleFrom(
                      minimumSize: const Size.fromHeight(48)),
                ),
          if (_resultMessage != null) ...[
            const SizedBox(height: 16),
            Text(_resultMessage!,
                style: TextStyle(
                    color: _resultMessage!.startsWith('Success')
                        ? Colors.green
                        : Colors.red)),
          ],
        ],
      ),
    );
  }
}

// ========== MANUAL INPUT TAB - COMPLETE ==========
class _ManualInputTab extends StatefulWidget {
  const _ManualInputTab();
  @override
  State<_ManualInputTab> createState() => _ManualInputTabState();
}

class _ManualInputTabState extends State<_ManualInputTab> {
  final _paperNameController = TextEditingController();
  final _totalQuestionsController = TextEditingController();
  final _answersController = TextEditingController();
  bool _loading = false;
  String? _message;

  Future<void> _submit() async {
    if (_paperNameController.text.trim().isEmpty ||
        _totalQuestionsController.text.trim().isEmpty ||
        _answersController.text.trim().isEmpty) {
      setState(() => _message = 'Error: Fill all fields');
      return;
    }

    setState(() {
      _loading = true;
      _message = null;
    });

    try {
      final res = await http.post(
        Uri.parse('${Config.apiBaseUrl}/api/manual-answer-key'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'paper_name': _paperNameController.text.trim(),
          'total_questions': int.parse(_totalQuestionsController.text.trim()),
          'answers': _answersController.text.trim(),
        }),
      );

      if (res.statusCode == 200) {
        setState(() {
          _message = 'Success: Answer key created!';
          _paperNameController.clear();
          _totalQuestionsController.clear();
          _answersController.clear();
        });
      } else {
        setState(() => _message = 'Error: ${res.body}');
      }
    } catch (e) {
      setState(() => _message = 'Error: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.green.shade50, Colors.green.shade100],
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.green.shade300, width: 2),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.edit_note, color: Colors.white, size: 32),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Manual Answer Key Entry',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.green.shade900,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Enter answers manually without uploading images',
                        style: TextStyle(fontSize: 14, color: Colors.green.shade700),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),

          // Paper Name
          Text(
            'Paper Name',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade800,
            ),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _paperNameController,
            style: const TextStyle(fontSize: 16),
            decoration: InputDecoration(
              hintText: 'e.g., Physics Mid-Term Exam 2024',
              prefixIcon: const Icon(Icons.description, size: 24),
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.grey.shade300, width: 2),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.grey.shade300, width: 2),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Colors.green, width: 2),
              ),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
            ),
          ),
          const SizedBox(height: 24),

          // Total Questions
          Text(
            'Total Questions',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade800,
            ),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _totalQuestionsController,
            keyboardType: TextInputType.number,
            style: const TextStyle(fontSize: 16),
            decoration: InputDecoration(
              hintText: 'e.g., 50',
              prefixIcon: const Icon(Icons.numbers, size: 24),
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.grey.shade300, width: 2),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.grey.shade300, width: 2),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Colors.green, width: 2),
              ),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
            ),
          ),
          const SizedBox(height: 24),

          // BIG Answer Input Box
          Text(
            'Answer Key (One answer per line)',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade800,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.green.shade300, width: 2),
              color: Colors.white,
            ),
            child: TextField(
              controller: _answersController,
              maxLines: 18,
              style: const TextStyle(fontSize: 15, height: 1.6),
              decoration: InputDecoration(
                hintText: 'Example:\n1-A\n2-B\n3-C,D\n4-A\n5-B,C,D\n6-A\n7-D\n8-B\n9-C\n10-A',
                hintStyle: TextStyle(color: Colors.grey.shade400, fontSize: 14),
                border: InputBorder.none,
                contentPadding: const EdgeInsets.all(20),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Format Guide
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.blue.shade200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.info, color: Colors.blue.shade700, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'Format Guide',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.blue.shade900,
                        fontSize: 15,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _buildFormatRow('Single Answer', '1-A, 2-B, 3-D'),
                const SizedBox(height: 6),
                _buildFormatRow('Multiple Answers', '4-A,C, 5-B,D, 6-A,B,C'),
                const SizedBox(height: 6),
                _buildFormatRow('One Per Line', 'Each question on new line'),
              ],
            ),
          ),
          const SizedBox(height: 28),

          // Submit Button
          _loading
              ? Container(
                  height: 60,
                  alignment: Alignment.center,
                  child: const CircularProgressIndicator(strokeWidth: 3),
                )
              : ElevatedButton(
                  onPressed: _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 18),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 3,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: const [
                      Icon(Icons.check_circle, size: 26),
                      SizedBox(width: 12),
                      Text(
                        'Create Answer Key',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),

          // Message Display
          if (_message != null) ...[
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _message!.startsWith('Success')
                    ? Colors.green.shade50
                    : Colors.red.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _message!.startsWith('Success')
                      ? Colors.green.shade300
                      : Colors.red.shade300,
                  width: 2,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _message!.startsWith('Success')
                        ? Icons.check_circle
                        : Icons.error,
                    color: _message!.startsWith('Success')
                        ? Colors.green.shade700
                        : Colors.red.shade700,
                    size: 28,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      _message!,
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 15,
                        color: _message!.startsWith('Success')
                            ? Colors.green.shade900
                            : Colors.red.shade900,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildFormatRow(String label, String example) {
    return Row(
      children: [
        Container(
          width: 6,
          height: 6,
          decoration: BoxDecoration(
            color: Colors.blue.shade700,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 8),
        Text(
          '$label: ',
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
        ),
        Text(
          example,
          style: TextStyle(color: Colors.grey.shade700, fontSize: 13),
        ),
      ],
    );
  }
}

// ========== MANAGE PAPERS TAB - COMPLETE ==========
class _ManagePapersTab extends StatefulWidget {
  const _ManagePapersTab();
  @override
  State<_ManagePapersTab> createState() => _ManagePapersTabState();
}

class _ManagePapersTabState extends State<_ManagePapersTab> {
  List<dynamic> _papers = [];
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadPapers();
  }

  Future<void> _loadPapers() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final res = await http.get(Uri.parse('${Config.apiBaseUrl}/api/papers'));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        setState(() {
          _papers = data['papers'] ?? [];
          _loading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to load';
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = '$e';
        _loading = false;
      });
    }
  }

  Future<void> _delete(int id, String name) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Delete Paper?'),
        content: Text('Delete "$name"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(c, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      await http.delete(Uri.parse('${Config.apiBaseUrl}/api/papers/$id'));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Deleted "$name"'), backgroundColor: Colors.green),
        );
        _loadPapers();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _viewDetails(dynamic p) async {
    try {
      final res = await http.get(
        Uri.parse('${Config.apiBaseUrl}/api/papers/${p['id']}/answers'),
      );
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        final ans = data['answers'] ?? [];
        if (mounted) {
          showDialog(
            context: context,
            builder: (c) => AlertDialog(
              title: Text(p['paper_name']),
              content: SizedBox(
                width: double.maxFinite,
                child: ListView.builder(
                  shrinkWrap: true,
                  itemCount: ans.length,
                  itemBuilder: (c, i) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.blue.shade100,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text('Q${ans[i]['question_number']}'),
                        ),
                        const SizedBox(width: 8),
                        const Icon(Icons.arrow_forward, size: 16),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.green.shade100,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(ans[i]['correct_option'] ?? ''),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(c),
                  child: const Text('Close'),
                ),
              ],
            ),
          );
        }
      }
    } catch (e) {
      // Handle error
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.purple.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.purple.shade200, width: 2),
          ),
          child: Row(
            children: [
              Icon(Icons.folder, color: Colors.purple.shade700, size: 28),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Manage ${_papers.length} papers',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
              ElevatedButton.icon(
                onPressed: _loadPapers,
                icon: const Icon(Icons.refresh, size: 18),
                label: const Text('Refresh'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.purple,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
        if (_loading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else if (_error != null)
          Expanded(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(_error!),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loadPapers,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          )
        else if (_papers.isEmpty)
          Expanded(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.inbox, size: 80, color: Colors.grey.shade300),
                  const SizedBox(height: 16),
                  Text(
                    'No papers yet',
                    style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
                  ),
                ],
              ),
            ),
          )
        else
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _papers.length,
              itemBuilder: (c, i) {
                final p = _papers[i];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  elevation: 2,
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16),
                    leading: CircleAvatar(
                      backgroundColor: Colors.purple.shade100,
                      child: Icon(Icons.description, color: Colors.purple.shade700),
                    ),
                    title: Text(
                      p['paper_name'] ?? 'Untitled',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                    subtitle: Text('${p['total_questions']} questions'),
                    trailing: PopupMenuButton(
                      itemBuilder: (c) => [
                        const PopupMenuItem(
                          value: 'view',
                          child: Row(
                            children: [
                              Icon(Icons.visibility, size: 20),
                              SizedBox(width: 8),
                              Text('View'),
                            ],
                          ),
                        ),
                        const PopupMenuItem(
                          value: 'delete',
                          child: Row(
                            children: [
                              Icon(Icons.delete, color: Colors.red, size: 20),
                              SizedBox(width: 8),
                              Text('Delete', style: TextStyle(color: Colors.red)),
                            ],
                          ),
                        ),
                      ],
                      onSelected: (v) {
                        if (v == 'view') _viewDetails(p);
                        if (v == 'delete') _delete(p['id'], p['paper_name']);
                      },
                    ),
                  ),
                );
              },
            ),
          ),
      ],
    );
  }
}
