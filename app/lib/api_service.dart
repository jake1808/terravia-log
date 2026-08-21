import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;


class ApiService{
 static String baseUrl = dotenv.env['API_BASE_URL'] ?? 'http://localhost:5000';
 

  // Register a new user
  static Future<Map<String,dynamic>> register(String name, String email, String password, String role) async{
    print('API Base URL: $baseUrl');
    final response = await http.post(
      Uri.parse('$baseUrl/register'),
      headers:{'Content-Type':'application/json'},
      body: jsonEncode({
        'name': name,
        'email': email,
        'password': password,
        'role': role
      })
    );
    return jsonDecode(response.body);
  }

  // login
  static Future<Map<String,dynamic>> login(String email, String password) async{
    final response = await http.post(
      Uri.parse('$baseUrl/login'),
      headers:{'Content-Type':'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password
      })
    );
    return jsonDecode(response.body);
  }

  // home
  static Future<Map<String,dynamic>> home(String token) async{
    final response = await http.get(
      Uri.parse('$baseUrl/'),
      headers:{
        'Content-Type':'application/json',
        'x-access-token': token
      }
    );
    if(response.statusCode == 200){
      return jsonDecode(response.body);
  }else{
      throw Exception('Failed to load data');
    }
  }
}