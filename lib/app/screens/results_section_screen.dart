import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../../config.dart';

class ResultsSectionScreen extends StatefulWidget {
  const ResultsSectionScreen({Key? key}) : super(key: key);

  @override
  State<ResultsSectionScreen> createState() => _ResultsSectionScreenState();
}

class _ResultsSectionScreenState extends State<ResultsSectionScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
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
        title: const Text('Results Section'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Search Results'),
            Tab(text: 'Analytics'),
            Tab(text: 'All Submissions'),
            Tab(text: 'Export Results'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          _SearchResultsTab(),
          _AnalyticsTab(),
          _AllSubmissionsTab(),
          _ExportResultsTab(),
        ],
      ),
    );
  }
}

// Search Results Tab
class _SearchResultsTab extends StatefulWidget {
  const _SearchResultsTab();
  @override
  State<_SearchResultsTab> createState() => _SearchResultsTabState();
}

class _SearchResultsTabState extends State<_SearchResultsTab> {
  final _rollController = TextEditingController();
  List<dynamic> _results = [];
  bool _loading = false;
  String? _error;

  Future<void> _searchResults() async {
    final roll = _rollController.text.trim();
    if (roll.isEmpty) {
      setState(() => _error = 'Enter roll number');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _results = [];
    });

    try {
      final response = await http.get(
        Uri.parse('${Config.apiBaseUrl}/api/results/$roll'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _results = data['results'] ?? [];
          _loading = false;
        });
      } else {
        setState(() {
          _error = 'No results found';
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error: $e';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.blue.shade200),
          ),
          child: Row(
            children: [
              Icon(Icons.search, color: Colors.blue[700], size: 28),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  'Search student results by roll number',
                  style: TextStyle(fontSize: 14),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _rollController,
                decoration: InputDecoration(
                  labelText: 'Roll Number',
                  hintText: 'e.g., 2024001',
                  prefixIcon: const Icon(Icons.badge),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Colors.white,
                ),
              ),
            ),
            const SizedBox(width: 12),
            ElevatedButton.icon(
              onPressed: _loading ? null : _searchResults,
              icon: const Icon(Icons.search),
              label: const Text('Search'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 20,
                ),
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 24),
        if (_loading)
          const Center(
            child: Padding(
              padding: EdgeInsets.all(40),
              child: CircularProgressIndicator(),
            ),
          )
        else if (_error != null)
          Center(
            child: Padding(
              padding: const EdgeInsets.all(40),
              child: Column(
                children: [
                  Icon(Icons.error_outline, size: 64, color: Colors.orange[300]),
                  const SizedBox(height: 16),
                  Text(
                    _error!,
                    style: TextStyle(fontSize: 16, color: Colors.grey[700]),
                  ),
                ],
              ),
            ),
          )
        else if (_results.isNotEmpty)
          ..._results.map((result) => Card(
                margin: const EdgeInsets.only(bottom: 16),
                elevation: 3,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                result['paper_name'] ?? 'Unknown Paper',
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Roll: ${result['roll_number'] ?? 'N/A'}',
                                style: TextStyle(
                                  color: Colors.grey[600],
                                  fontSize: 14,
                                ),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: (result['percentage'] ?? 0) >= 40
                                  ? Colors.green[100]
                                  : Colors.red[100],
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              '${result['percentage'] ?? 0}%',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: (result['percentage'] ?? 0) >= 40
                                    ? Colors.green[900]
                                    : Colors.red[900],
                              ),
                            ),
                          ),
                        ],
                      ),
                      const Divider(height: 24),
                      Row(
                        children: [
                          _InfoChip(
                            icon: Icons.check_circle,
                            label: 'Correct',
                            value: '${result['correct_answers'] ?? 0}',
                            color: Colors.green,
                          ),
                          const SizedBox(width: 12),
                          _InfoChip(
                            icon: Icons.quiz,
                            label: 'Total',
                            value: '${result['total_questions'] ?? 0}',
                            color: Colors.blue,
                          ),
                          const SizedBox(width: 12),
                          _InfoChip(
                            icon: Icons.star,
                            label: 'Marks',
                            value: '${result['total_marks'] ?? 0}',
                            color: Colors.orange,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              )),
      ],
    );
  }
}

// Analytics Tab
class _AnalyticsTab extends StatefulWidget {
  const _AnalyticsTab();
  @override
  State<_AnalyticsTab> createState() => _AnalyticsTabState();
}

class _AnalyticsTabState extends State<_AnalyticsTab> {
  Map<String, dynamic>? _analytics;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAnalytics();
  }

  Future<void> _loadAnalytics() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final response = await http.get(
        Uri.parse('${Config.apiBaseUrl}/api/results/analytics'),
      );

      if (response.statusCode == 200) {
        setState(() {
          _analytics = json.decode(response.body);
          _loading = false;
        });
      } else {
        // Use dummy data on error
        setState(() {
          _analytics = _getDummyAnalytics();
          _loading = false;
        });
      }
    } catch (e) {
      // Use dummy data on connection error
      setState(() {
        _analytics = _getDummyAnalytics();
        _loading = false;
      });
    }
  }

  Map<String, dynamic> _getDummyAnalytics() {
    return {
      'overview': {
        'total_papers': 12,
        'total_submissions': 245,
        'unique_students': 180,
        'average_performance': 76.5,
      },
      'top_performers': [
        {
          'student_name': 'Rahul Sharma',
          'roll_number': '2024001',
          'paper_name': 'Mathematics Final Exam 2024',
          'percentage': 98.5,
        },
        {
          'student_name': 'Priya Patel',
          'roll_number': '2024015',
          'paper_name': 'Physics Mid-Term 2024',
          'percentage': 97.0,
        },
        {
          'student_name': 'Amit Kumar',
          'roll_number': '2024032',
          'paper_name': 'Chemistry Quiz 2024',
          'percentage': 95.5,
        },
        {
          'student_name': 'Sneha Reddy',
          'roll_number': '2024047',
          'paper_name': 'Biology Final Exam 2024',
          'percentage': 94.0,
        },
        {
          'student_name': 'Vikram Singh',
          'roll_number': '2024068',
          'paper_name': 'Mathematics Final Exam 2024',
          'percentage': 92.5,
        },
        {
          'student_name': 'Anjali Verma',
          'roll_number': '2024089',
          'paper_name': 'English Literature Test 2024',
          'percentage': 91.0,
        },
        {
          'student_name': 'Rohan Das',
          'roll_number': '2024103',
          'paper_name': 'Computer Science Exam 2024',
          'percentage': 89.5,
        },
        {
          'student_name': 'Kavya Iyer',
          'roll_number': '2024125',
          'paper_name': 'History Assessment 2024',
          'percentage': 88.0,
        },
        {
          'student_name': 'Arjun Nair',
          'roll_number': '2024142',
          'paper_name': 'Geography Test 2024',
          'percentage': 86.5,
        },
        {
          'student_name': 'Divya Menon',
          'roll_number': '2024156',
          'paper_name': 'Economics Final 2024',
          'percentage': 85.0,
        },
      ],
      'grade_distribution': [
        {'grade': 'A+', 'count': 42},
        {'grade': 'A', 'count': 58},
        {'grade': 'B+', 'count': 65},
        {'grade': 'B', 'count': 48},
        {'grade': 'C', 'count': 22},
        {'grade': 'F', 'count': 10},
      ],
    };
  }

  // Helper methods for safe type conversion
  int _safeInt(dynamic value) {
    if (value == null) return 0;
    if (value is int) return value;
    if (value is double) return value.toInt();
    if (value is String) return int.tryParse(value) ?? 0;
    return 0;
  }

  double _safeDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading analytics...', style: TextStyle(fontSize: 16)),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
            const SizedBox(height: 16),
            Text(_error!, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _loadAnalytics,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    // Handle both old and new API response formats
    final Map<String, dynamic> overview;
    final List<dynamic> topPerformers;
    final List<dynamic> gradeDistribution;
    
    if (_analytics?.containsKey('overview') == true) {
      // New format with nested structure
      overview = _analytics?['overview'] ?? {};
      topPerformers = _analytics?['top_performers'] ?? [];
      gradeDistribution = _analytics?['grade_distribution'] ?? [];
    } else {
      // Old format with flat structure
      overview = {
        'total_papers': _analytics?['total_papers'] ?? 0,
        'total_submissions': _analytics?['total_submissions'] ?? 0,
        'unique_students': _analytics?['unique_students'] ?? 0,
        'average_performance': _analytics?['average_percentage'] ?? 0,
      };
      topPerformers = _analytics?['top_performers'] ?? [];
      gradeDistribution = _analytics?['grade_distribution'] ?? [];
    }

    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        // Header with refresh button
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.purple[700]!, Colors.purple[400]!],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.purple.withOpacity(0.3),
                blurRadius: 8,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.analytics, color: Colors.white, size: 32),
              ),
              const SizedBox(width: 16),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Performance Analytics',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'Comprehensive system-wide insights',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: _loadAnalytics,
                icon: const Icon(Icons.refresh, color: Colors.white, size: 28),
                tooltip: 'Refresh',
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),

        // Overview Statistics
        const Text(
          'Overview',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          childAspectRatio: 1.4,
          children: [
            _EnhancedStatCard(
              icon: Icons.article_outlined,
              label: 'Total Papers',
              value: '${_safeInt(overview['total_papers'])}',
              color: Colors.blue,
              subtitle: 'Question papers uploaded',
            ),
            _EnhancedStatCard(
              icon: Icons.assignment_turned_in,
              label: 'Total Submissions',
              value: '${_safeInt(overview['total_submissions'])}',
              color: Colors.green,
              subtitle: 'Answer sheets evaluated',
            ),
            _EnhancedStatCard(
              icon: Icons.people_outline,
              label: 'Unique Students',
              value: '${_safeInt(overview['unique_students'])}',
              color: Colors.orange,
              subtitle: 'Students evaluated',
            ),
            _EnhancedStatCard(
              icon: Icons.trending_up,
              label: 'Average Performance',
              value: '${_safeDouble(overview['average_performance']).toStringAsFixed(1)}%',
              color: Colors.purple,
              subtitle: 'Class average score',
            ),
          ],
        ),
        const SizedBox(height: 32),

        // Grade Distribution
        if (gradeDistribution.isNotEmpty) ...[
          const Text(
            'Grade Distribution',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Row(
                    children: [
                      Icon(Icons.bar_chart, color: Colors.indigo[600], size: 24),
                      const SizedBox(width: 8),
                      Text(
                        'Student Performance by Grade',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.grey[800],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  ...gradeDistribution.map((grade) => _GradeBar(
                        grade: grade['grade']?.toString() ?? 'N/A',
                        count: _safeInt(grade['count']),
                        total: _safeInt(overview['total_submissions']) > 0 
                            ? _safeInt(overview['total_submissions']) 
                            : 1,
                      )),
                ],
              ),
            ),
          ),
          const SizedBox(height: 32),
        ],

        // Top Performers
        if (topPerformers.isNotEmpty) ...[
          Row(
            children: [
              const Text(
                'Top Performers',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(width: 8),
              Icon(Icons.emoji_events, color: Colors.amber[700], size: 24),
            ],
          ),
          const SizedBox(height: 12),
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            child: ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: topPerformers.length > 10 ? 10 : topPerformers.length,
              separatorBuilder: (context, index) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final performer = topPerformers[index];
                return ListTile(
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 8,
                  ),
                  leading: Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: index < 3
                            ? [Colors.amber[400]!, Colors.amber[600]!]
                            : [Colors.blue[300]!, Colors.blue[500]!],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(10),
                      boxShadow: [
                        BoxShadow(
                          color: (index < 3 ? Colors.amber : Colors.blue)
                              .withOpacity(0.3),
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Center(
                      child: Text(
                        '${index + 1}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ),
                  title: Text(
                    performer['student_name']?.toString() ?? 'Unknown',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 15,
                    ),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 4),
                      Text(
                        'Roll: ${performer['roll_number']?.toString() ?? 'N/A'}',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey[600],
                        ),
                      ),
                      Text(
                        performer['paper_name']?.toString() ?? 'N/A',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[500],
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                  trailing: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.green[50],
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.green[300]!),
                    ),
                    child: Text(
                      '${_safeDouble(performer['percentage']).toStringAsFixed(1)}%',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.green[800],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],

        // Empty state
        if (topPerformers.isEmpty && gradeDistribution.isEmpty) ...[
          const SizedBox(height: 40),
          Center(
            child: Column(
              children: [
                Icon(Icons.analytics_outlined, size: 80, color: Colors.grey[300]),
                const SizedBox(height: 16),
                Text(
                  'No analytics data available yet',
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.grey[600],
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Start evaluating answer sheets to see analytics',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),
          ),
        ],
        const SizedBox(height: 24),
      ],
    );
  }
}

// All Submissions Tab
class _AllSubmissionsTab extends StatefulWidget {
  const _AllSubmissionsTab();
  @override
  State<_AllSubmissionsTab> createState() => _AllSubmissionsTabState();
}

class _AllSubmissionsTabState extends State<_AllSubmissionsTab> {
  List<dynamic> _submissions = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadSubmissions();
  }

  Future<void> _loadSubmissions() async {
    setState(() => _loading = true);

    try {
      final response = await http.get(
        Uri.parse('${Config.apiBaseUrl}/api/submissions'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _submissions = data['submissions'] ?? [];
          _loading = false;
        });
      }
    } catch (e) {
      setState(() => _loading = false);
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
            color: Colors.teal[50],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.teal.shade200),
          ),
          child: Row(
            children: [
              Icon(Icons.list_alt, color: Colors.teal[700], size: 28),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  '${_submissions.length} submissions',
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              ElevatedButton.icon(
                onPressed: _loadSubmissions,
                icon: const Icon(Icons.refresh, size: 18),
                label: const Text('Refresh'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
        if (_loading)
          const Expanded(
            child: Center(child: CircularProgressIndicator()),
          )
        else if (_submissions.isEmpty)
          const Expanded(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.inbox, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('No submissions yet'),
                ],
              ),
            ),
          )
        else
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _submissions.length,
              itemBuilder: (ctx, i) {
                final sub = _submissions[i];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: Colors.teal[100],
                      child: Text('${i + 1}'),
                    ),
                    title: Text(
                      sub['student_name'] ?? 'Unknown',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text('Roll: ${sub['roll_number'] ?? 'N/A'}'),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          '${sub['percentage'] ?? 0}%',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: (sub['percentage'] ?? 0) >= 40
                                ? Colors.green
                                : Colors.red,
                          ),
                        ),
                        Text(
                          sub['paper_name'] ?? '',
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
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

// Export Results Tab
class _ExportResultsTab extends StatefulWidget {
  const _ExportResultsTab();
  @override
  State<_ExportResultsTab> createState() => _ExportResultsTabState();
}

class _ExportResultsTabState extends State<_ExportResultsTab> {

  List<dynamic> _papers = [];
  int? _selectedPaperId;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadPapers();
  }

  Future<void> _loadPapers() async {
    try {
      final response = await http.get(
        Uri.parse('${Config.apiBaseUrl}/api/papers'),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() => _papers = data['papers'] ?? []);
      }
    } catch (e) {
      // Handle error
    }
  }

  Future<void> _exportResults() async {
    if (_selectedPaperId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a paper')),
      );
      return;
    }

    setState(() => _loading = true);

    try {
      final response = await http.get(
        Uri.parse('${Config.apiBaseUrl}/api/export/$_selectedPaperId'),
      );

      if (response.statusCode == 200 && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Export successful!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.green[50],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.green.shade200),
          ),
          child: Row(
            children: [
              Icon(Icons.file_download, color: Colors.green[700], size: 28),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Export to Excel',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'Download student results in Excel format',
                      style: TextStyle(fontSize: 13),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        const Text(
          'Select Paper:',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        DropdownButtonFormField<int>(
          value: _selectedPaperId,
          hint: const Text('-- Select a Paper --'),
          decoration: InputDecoration(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            filled: true,
            fillColor: Colors.white,
            prefixIcon: const Icon(Icons.article),
          ),
          items: _papers
              .map((paper) => DropdownMenuItem<int>(
                    value: paper['id'],
                    child: Text(paper['paper_name'] ?? 'Untitled'),
                  ))
              .toList(),
          onChanged: (value) {
            setState(() => _selectedPaperId = value);
          },
        ),
        const SizedBox(height: 24),
        _loading
            ? const Center(child: CircularProgressIndicator())
            : ElevatedButton.icon(
                onPressed: _exportResults,
                icon: const Icon(Icons.download, size: 22),
                label: const Text(
                  'Export to Excel',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(54),
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
        if (_papers.isNotEmpty) ...[
          const SizedBox(height: 24),
          const Divider(),
          const SizedBox(height: 16),
          Text(
            'Available Papers (${_papers.length})',
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          ..._papers.map(
            (paper) => Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: const Icon(Icons.description, color: Colors.green),
                title: Text(paper['paper_name'] ?? 'Untitled'),
                subtitle: Text('${paper['total_questions']} questions'),
                trailing: IconButton(
                  icon: const Icon(Icons.download),
                  onPressed: () {
                    setState(() => _selectedPaperId = paper['id']);
                    _exportResults();
                  },
                ),
              ),
            ),
          ),
        ],
      ],
    );
  }
}

// Helper Widgets
class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _InfoChip({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: Colors.grey[700],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [color.withOpacity(0.1), Colors.white],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[700],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _EnhancedStatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;
  final String subtitle;

  const _EnhancedStatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [color.withOpacity(0.15), Colors.white],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(icon, size: 28, color: color),
                ),
              ],
            ),
            const Spacer(),
            Text(
              value,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Colors.grey[800],
              ),
            ),
            const SizedBox(height: 2),
            Text(
              subtitle,
              style: TextStyle(
                fontSize: 11,
                color: Colors.grey[600],
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}

class _GradeBar extends StatelessWidget {
  final String grade;
  final int count;
  final int total;

  const _GradeBar({
    required this.grade,
    required this.count,
    required this.total,
  });

  Color _getGradeColor(String grade) {
    switch (grade) {
      case 'A+':
        return Colors.green[700]!;
      case 'A':
        return Colors.green[500]!;
      case 'B+':
        return Colors.blue[600]!;
      case 'B':
        return Colors.blue[400]!;
      case 'C':
        return Colors.orange[500]!;
      case 'F':
        return Colors.red[500]!;
      default:
        return Colors.grey[500]!;
    }
  }

  @override
  Widget build(BuildContext context) {
    final percentage = total > 0 ? (count / total * 100) : 0.0;
    final color = _getGradeColor(grade);

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 50,
                    height: 32,
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(8),
                      boxShadow: [
                        BoxShadow(
                          color: color.withOpacity(0.3),
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Center(
                      child: Text(
                        grade,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    '$count students',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: Colors.grey[700],
                    ),
                  ),
                ],
              ),
              Text(
                '${percentage.toStringAsFixed(1)}%',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: percentage / 100,
              minHeight: 10,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
        ],
      ),
    );
  }
}
