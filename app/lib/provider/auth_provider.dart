import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../api_service.dart';

class AuthProvider with ChangeNotifier{
  bool _isLoading = false;
  bool _isOfflineMode = false;
  Map<String, dynamic>? _user;
  String? _token;

  // Getters
  bool get isLoading => _isLoading;
  bool get isOfflineMode => _isOfflineMode;
  Map<String, dynamic>? get user => _user;
  String? get token => _token;
  bool get isAuthenticated => _token != null;

  // Auto login when app starts
  Future<void> tryAutoLogin() async{
    _isLoading = true;
    notifyListeners();

    final prefs = await SharedPreferences.getInstance();
    final savedToken = prefs.getString('token');
    final savedUser = prefs.getString('user');

    if(savedToken != null && savedUser != null){
      _token = savedToken;
      _user = jsonDecode(savedUser);
      _isOfflineMode = true;

      try{
        final freshData = await ApiService.home(_token!);
        _user = freshData['user'];
        _isOfflineMode = false;
        prefs.setString('user', jsonEncode(_user));
      } catch(e){
        print("Offline mode activated: $e");
      }
    }
    _isLoading = false;
    notifyListeners();
  }
  // Login
  Future<bool> login(String email, String password) async{
    _isLoading = true;
    notifyListeners();

    try{
      final response = await ApiService.login(email, password);

      if(response.containsKey('token')){
        _token = response['token'];
        _user = response['user'];
        _isOfflineMode = false;

        final prefs = await SharedPreferences.getInstance();
        prefs.setString('token', _token!);
        prefs.setString('user', jsonEncode(_user));

        _isLoading = false;
        notifyListeners();
        return true;
      } else{
        _isLoading = false;
        notifyListeners();
        throw Exception(response['message'] ?? 'Login failed');
      }
    } catch(e){
      _isLoading = false;
      notifyListeners();
      rethrow;
    }
  }

  // Logout
  Future<void> logout() async{
    _token = null;
    _user = null;
    _isOfflineMode = false;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('user');

    notifyListeners();
  }
}