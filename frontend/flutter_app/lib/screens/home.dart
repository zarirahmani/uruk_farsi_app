import 'package:flutter/material.dart';
import 'handwriting.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Farsi Writing Tutor'),
      ),
      body: Center(
        child: ElevatedButton(
          child: const Text('Start Handwriting Practice'),
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => const HandwritingScreen(),
              ),
            );
          },
        ),
      ),
    );
  }
}