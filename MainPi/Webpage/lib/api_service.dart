import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

const BASE_URL = 'http://localhost:8080';

class Task {
  final int taskId;
  final String name;
  final String description;
  final DateTime dueDate;
  bool isDone = false;

  Task({ required this.taskId, required this.name, required this.description, required this.dueDate, isDone});

  factory Task.fromJson(Map<String, dynamic> json) {
    var dateFormatter = DateFormat('dd.MM.yyyy');
    return Task(
      taskId: int.parse(json['taskId'].toString()),
      name: json['name'],
      description: json['description'],
      dueDate: dateFormatter.parse(json['dueDate'])
    );
  }

  Map<String, dynamic> toJson() {
     var dateFormatter = DateFormat('dd.MM.yyyy');
    return {
      'taskId': taskId.toString(),
      'name': name,
      'description': description,
      'dueDate': dateFormatter.format(dueDate)
    };
  }
}

class User {
  final String name;

  User({required this.name});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      name: json['name']
    );
  }
  Map<String, dynamic> toJson() {
    return {
      'name': name
    };
  }
}

class ApiService {
  static Future<List<User>> getUsers() async {
  
    const String url = '$BASE_URL/getAllPerson';
  
    final response = await http.get(Uri.parse(url));
    if (response.statusCode == 200) {
        final jsonData = json.decode(response.body) as List<dynamic>;
        final users = jsonData.map((userJson) => User(name:userJson)).toList();
        return users;
    }
   
    throw Exception('Failed to get users.');
    
  }

   static Future<List<Task>> getTasksByUserAndDate(User user, DateTime date) async {
    DateFormat dateFormatter = DateFormat('dd.MM.yyyy');
    String url = '$BASE_URL/getData';
    Uri finalUrl = Uri.parse('$url/${user.name}/${dateFormatter.format(date)}');
    final response = await http.get(finalUrl);
    if (response.statusCode == 200) {
        final jsonData = json.decode(response.body) as List<dynamic>;
        final tasks = jsonData.map((taskJson) => Task.fromJson(taskJson)).toList();
        return tasks;
    }
   
    throw Exception('Failed to get tasks.');
    
  }

  static Future<User> addUser(User user, String profileImage) async {
    final String url = '$BASE_URL/addImage/${user.name}';
    final response = await http.post(
      Uri.parse(url), body: profileImage
    );
        if (response.statusCode == 200 || response.statusCode == 201) {
        final jsonData = json.decode(response.body) as dynamic;
        final user= User(name: jsonData);
        
        return user;
    }
   
    throw Exception('Failed to add user. ${response.statusCode}');
  }

   static Future<Task> addTask(Task task) async {
    const String url = '$BASE_URL/addTask';
    final response = await http.post(
      Uri.parse(url), body: task.toJson()
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      final jsonData = json.decode(response.body) as dynamic;
      final task= Task.fromJson(jsonData);
        
      return task;
    }
   
    throw Exception('Failed to add task. ${response.statusCode}');
  }

}