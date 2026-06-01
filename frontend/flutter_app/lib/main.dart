
import 'package:flutter/material.dart';
import 'screens/home.dart';

void main() {
  runApp(const FarsiApp());
}

class FarsiApp extends StatelessWidget {
  const FarsiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Farsi Writing Tutor',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.indigo,
      ),
      home: const HomeScreen(),
    );
  }
}
