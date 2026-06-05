import 'package:flutter/material.dart';

import 'lessons.dart';
import 'handwriting.dart';
import 'progress.dart';
import 'admin_dashboard.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  void goTo(BuildContext context, Widget screen) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => screen),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Farsi Writing Tutor'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Welcome to Farsi Writing Tutor',
              style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 32),

            ElevatedButton(
              onPressed: () => goTo(context, const LessonsScreen()),
              child: const Text('Lessons'),
            ),

            const SizedBox(height: 12),

            ElevatedButton(
              onPressed: () => goTo(context, const HandwritingScreen()),
              child: const Text('Handwriting Practice'),
            ),

            const SizedBox(height: 12),

            ElevatedButton(
              onPressed: () => goTo(context, const ProgressScreen()),
              child: const Text('Progress'),
            ),

            const SizedBox(height: 12),

            OutlinedButton(
              onPressed: () => goTo(context, const AdminDashboardScreen()),
              child: const Text('Admin Dashboard'),
            ),
          ],
        ),
      ),
    );
  }
}
