import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../provider/auth_provider.dart';
import 'home_screen.dart';

class LoginScreen extends StatefulWidget{
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen>{
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  Future<void>_submit() async{
    final authProvider = Provider.of<AuthProvider>(context, listen:false);

    try{
      await authProvider.login(_emailController.text, _passwordController.text);
      // Navigator.pushReplacement(context, MaterialPageRoute(builder: (context)=>HomeScreen()));
    } catch(e){
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Login failed: $e')));
    }
  }
  @override
  Widget build(BuildContext context){
    return Scaffold(
      appBar: AppBar(title: Text('Login')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Consumer<AuthProvider>(
          builder:(context, auth, child){
            return Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children:[
                  TextField(controller: _emailController, decoration: InputDecoration(labelText:'Email')),
                  TextField(controller: _passwordController, decoration: InputDecoration(labelText:'Password'), obscureText:true),
                  SizedBox(height:20),
                  auth.isLoading
                  ? CircularProgressIndicator()
                  : ElevatedButton(onPressed:_submit, child: Text('Login'))
              ]
            );
          }
        )
      )
    );
  }
}