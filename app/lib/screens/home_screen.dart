import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../provider/auth_provider.dart';
import 'login_screen.dart';

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    
    return Scaffold(
      appBar: AppBar(
        title: Text('Home'),
        actions: [
          if (authProvider.isOfflineMode)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Center(child: Text('⚠️ Offline', style: TextStyle(color: Colors.orange))),
            ),
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () {
              authProvider.logout();
              Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => LoginScreen()));
            },
          )
        ],
      ),
      body: Center(
        child: authProvider.user == null
            ? Text('No user data found.')
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('Welcome, ${authProvider.user!['name']}!', style: TextStyle(fontSize: 24)),
                  SizedBox(height: 10),
                  Text('Email: ${authProvider.user!['email']}'),
                ],
              ),
      ),
    );
  }
}