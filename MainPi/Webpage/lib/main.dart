import 'dart:convert';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:file_picker/file_picker.dart';
import 'api_service.dart';


void main() => runApp(DashboardApp());

class UserFormDialog extends StatefulWidget {
  final double formWidth;
  UserFormDialog({required this.formWidth});
  @override
  _UserFormDialogState createState() => _UserFormDialogState();
}

class _UserFormDialogState extends State<UserFormDialog> {
  final TextEditingController _nameController = TextEditingController();
  bool _formValid = true;
  User? _user;
  PlatformFile? _selectedFile = null;

  _UserFormDialogState();

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  void _handleAddButtonPressed() async {
    if (_nameController.text.isEmpty || _selectedFile == null) {
      setState(() {
        _formValid = false;
      });
    } else {
      String profileImage = base64.encode(_selectedFile!.bytes!);
      final user = await ApiService.addUser(User( name: _nameController.text), profileImage);
      setState(() {
        _user =  user;
        _formValid = true;
      });
      
      // ignore: use_build_context_synchronously
      Navigator.of(context).pop(_user);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(24.0),
      ),
      content: Container(
        width: widget.formWidth,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
                decoration: InputDecoration(
                    hintText: "Name",
                    filled: true,
                    fillColor: Colors.grey[200],
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16.0),
                    ),
                     errorText: _nameController.text.isEmpty && !_formValid
                    ? 'Enter your name'
                    : null,
                    ),
                controller: _nameController,
            ),
            SizedBox(
              height: 20,
            ),
            Text(_selectedFile?.name ?? ""),
              SizedBox(
              height: 20,
            ),
            TextButton(
                style: TextButton.styleFrom(
                  padding: EdgeInsets.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                onPressed: ()  async {
                  var picked = await FilePicker.platform.pickFiles(type: FileType.image);
                  
                  if (picked != null) {
                    setState(() {
                       _selectedFile = picked.files.first;    
                    });
                  
                  }
                },
                child: Container(
                  width: double.infinity,
                  padding: EdgeInsets.symmetric(vertical: 15, horizontal: 20),
                  decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(16),
                      color: Colors.deepPurpleAccent),
                  child: Center(
                    child: Text(
                      'Upload photo',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ),)
          ],
        ),
      ),
      title: Row(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Add new user'),
            IconButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  _nameController.clear();
                },
                icon: Icon(Icons.close))
          ]),
      actions: <Widget>[
        TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _nameController.clear();
            },
            child: Text('Cancel')),
        TextButton(
          onPressed: () async {
            _handleAddButtonPressed();
          //  Navigator.of(context).pop(_user);
          },
          child: Container(
            padding: EdgeInsets.symmetric(vertical: 10, horizontal: 20),
            decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16), // radius of 10
                color: Colors.deepPurpleAccent // green as background color
                ),
            child: Text(
              'Add',
              style: TextStyle(color: Colors.white),
            ),
          ),
        )
      ],
    );
  }
}



class DashboardApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
          primarySwatch: MaterialColor(
            Colors.deepPurpleAccent.value,
            <int, Color>{
              50: Colors.deepPurpleAccent.withOpacity(0.1),
              100: Colors.deepPurpleAccent.withOpacity(0.2),
              200: Colors.deepPurpleAccent.withOpacity(0.3),
              300: Colors.deepPurpleAccent.withOpacity(0.4),
              400: Colors.deepPurpleAccent.withOpacity(0.5),
              500: Colors.deepPurpleAccent.withOpacity(0.6),
              600: Colors.deepPurpleAccent.withOpacity(0.7),
              700: Colors.deepPurpleAccent.withOpacity(0.8),
              800: Colors.deepPurpleAccent.withOpacity(0.9),
              900: Colors.deepPurpleAccent.withOpacity(1),
            },
          ),
          fontFamily: 'Nunito'),
      debugShowCheckedModeBanner: false,
      home: DashboardScreen(),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;
  User? _passedArgument;

  late List<Widget> _pages = [
    HomeScreen(onPageSelected: _onPageSelected, user: _passedArgument),
    ProfileScreen(user: _passedArgument),
  ];

  void _onPageSelected(int index, [User? user]) {
    setState(() {
      _selectedIndex = index;
      _passedArgument = user;
    });
    _pages = [
      HomeScreen(onPageSelected: _onPageSelected, user: _passedArgument),
      ProfileScreen(user: _passedArgument),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          SideNav(
            onPageSelected: _onPageSelected,
            isHomeSelected: _selectedIndex == 0,
          ),
          Expanded(
            flex: 8,
            child: _pages[_selectedIndex],
          ),
        ],
      ),
    );
  }
}

class SideNav extends StatelessWidget {
  final Function(int, [User?]) onPageSelected;
  final bool isHomeSelected;
  SideNav({required this.onPageSelected, required this.isHomeSelected});

  Future<User?> showAddUserDialog(BuildContext context) async {
  return await showDialog<User>(
      context: context,
      builder: (context) {
        return StatefulBuilder(builder: (context, setState) {
          var width = MediaQuery.of(context).size.width;
          var dialogWidth = max(width / 5, 500);
          return UserFormDialog(formWidth: dialogWidth.toDouble());
        });
      });
}

  @override
  Widget build(BuildContext context) {
    User? _newUser;

    Future<void> _handleNewProfilePressed() async {
       _newUser = await showAddUserDialog(context);
       if (isHomeSelected) onPageSelected(0, _newUser);
    }
    return Container(
        constraints: new BoxConstraints(
          minWidth: 100.0,
          maxWidth: 220.0,
        ),
        child: Ink(
          color: Colors.white,
          child: ListView(
            children: [
              const ListTile(
                title: Text("SmartReminder",
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
                    softWrap: false),
              ),
              ListTile(
                leading: const Icon(Icons.home, color: Colors.white),
                title: const Text('Home',
                    style: TextStyle(color: Colors.white), softWrap: false),
                selected: true,
                selectedTileColor: Colors.deepPurpleAccent,
                onTap: () {
                  onPageSelected(0);
                },
              ),
              ListTile(
                leading: const Icon(Icons.add_box_outlined,
                    color: Colors.deepPurpleAccent),
                title: const Text('New Profile',
                    style: TextStyle(color: Colors.deepPurpleAccent),
                    softWrap: false),
                onTap: () { _handleNewProfilePressed(); }
                ,
              ),
            ],
          ),
        ));
  }
}

class HomeScreen extends StatefulWidget {
  final Function(int, User?) onPageSelected;
  User? user;
   HomeScreen({required this.onPageSelected, this.user});
   @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
   List<User> _users = [];
   final Map<User, List<Task>> _userTasks = {};
  

  @override
  void didUpdateWidget(HomeScreen oldWidget) {
    if (widget.user != oldWidget.user && widget.user != null) {
      // Argument has changed, update the state
      _users.add(widget.user!);
      // fetch user here TODO
    }
    super.didUpdateWidget(oldWidget);
  }


    @override
  void initState() {
    super.initState();
    _fetchUsers().then(
      (users) =>
      users.forEach((user) { _fetchTasks(user); }) 
    );
  }

  

  Future<void> _fetchTasks(User user) async {
      final response = await ApiService.getTasksByUserAndDate(user, DateTime.now());
    setState(() {
      _userTasks[user] = response; 
    });
  }

  Future<List<User>> _fetchUsers() async {
    final response = await ApiService.getUsers();
    setState(() {
      _users = response;
    });
    return response;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color.fromARGB(20, 217, 207, 223),
      child: GridView.builder(
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: _calculateCrossAxisCount(context),
              crossAxisSpacing: 50.0,
              mainAxisSpacing: 50.0,
              childAspectRatio: 1.5),
          padding: const EdgeInsets.all(30.0),
          itemCount: _users.length,
          itemBuilder: (context, index) {
            return RoundedCard(user: _users[index], tasks: _userTasks[_users[index]], onPageSelected: widget.onPageSelected);
          }),
    );
  }

  int _calculateCrossAxisCount(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    const itemWidth = 500.0; // Adjust this value based on your card width
    final crossAxisCount = screenWidth ~/ itemWidth;
    return crossAxisCount;
  }
}

class RoundedCard extends StatelessWidget {
  final User user;
  final List<Task>? tasks;
  final Function(int, User) onPageSelected;

  RoundedCard({required this.user, required this.tasks,required this.onPageSelected});

  @override
  Widget build(BuildContext context) {
    return Card(
      shadowColor: Colors.transparent,
      elevation: null,
      color: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(24.0),
      ),
      child: Padding(
        padding: const EdgeInsets.only(left: 20, right: 20, top: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                 CircleAvatar(
                  backgroundColor: Colors.deepPurpleAccent,
                  child: Text(user.name[0], style: TextStyle(color: Colors.white)),
                ),
                const SizedBox(width: 10),
                Text(
                  user.name,
                  style: const TextStyle(fontSize: 20.0),
                ),
              ],
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 10),
                child: ScrollConfiguration(
                    behavior: ScrollConfiguration.of(context)
                        .copyWith(scrollbars: false),
                    child: SingleChildScrollView(
                        physics: const NeverScrollableScrollPhysics(),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Todays todolist',
                              style: TextStyle(
                                  fontSize: 24, fontWeight: FontWeight.w700),
                            ),
                            ...?tasks?.map((t) => Text(
                              t.name,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis
                              )).toList()
                          
                          ],
                        ),),),
              ),
            ),
            Container(
              color: Colors.white,
              padding: const EdgeInsets.only(bottom: 20),
              child: Row(
                mainAxisSize: MainAxisSize.max,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Container(
                    decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16), 
                        color:
                            Colors.deepPurpleAccent
                        ),
                    child: IconButton(
                      padding: const EdgeInsets.symmetric(
                          vertical: 10, horizontal: 20),
                      color: Colors.white,
                      onPressed: () {
                        onPageSelected(1, user);
                      },
                      icon: const Icon(Icons.east),
                    ),
                  )
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}

class ProfileScreen extends StatefulWidget {
  final User? user;
  ProfileScreen({required this.user});

  @override
  _ProfileState createState() => _ProfileState();

}
class _ProfileState extends State<ProfileScreen> {
  DateTime _selectedDate = DateTime.now();
  List<Task> _tasksByDate = [];
  
    @override
  void initState() {
    super.initState();
    _fetchTasks(_selectedDate);
  }
  
  void _addNewTask(Task task) async {  
    final _task = await ApiService.addTask(task);
      setState(() {
        _tasksByDate.add(_task);
      });
    
  }

  Future<void> _fetchTasks(DateTime date) async {
     final tasks = await ApiService.getTasksByUserAndDate(widget.user!, date);
    setState(() {
      _tasksByDate = tasks;
    });
  
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: EdgeInsets.all(30),
        child: Column(
            mainAxisSize: MainAxisSize.max,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    backgroundColor: Colors.deepPurpleAccent,
                    child: Text(widget.user?.name[0] ?? '', style: const TextStyle(color: Colors.white)),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    widget.user?.name ?? '',
                    style: const TextStyle(fontSize: 20.0),
                  ),
                ],
              ),
              SizedBox(height: 30),
              Expanded(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  mainAxisSize: MainAxisSize.max,
                  children: [
                    Expanded(
                      child: Card(
                        shadowColor: Colors.transparent,
                        elevation: null,
                        color: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24.0),
                        ),
                        child: Padding(
                            padding: const EdgeInsets.all(20),
                            child: CalendarDatePicker(
                              initialDate: DateTime.now(),
                              firstDate: DateTime.now()
                                  .subtract(Duration(days: 100000)),
                              lastDate:
                                  DateTime.now().add(Duration(days: 100000)),
                              onDateChanged: (DateTime value) {
                                setState(() {
                                  _selectedDate = value;
                                });
                                _fetchTasks(_selectedDate);
                              },
                            )),
                      ),
                    ),
                    SizedBox(
                      width: 30,
                    ),
                    Expanded(
                      child: Card(
                        shadowColor: Colors.transparent,
                        elevation: null,
                        color: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24.0),
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: TaskForm(selectedDate: _selectedDate, addNewTask: _addNewTask),
                        ),
                      ),
                    )
                  ],
                ),
              ),
              SizedBox(height: 30),
              Expanded(
                child: Card(
                  shadowColor: Colors.transparent,
                  elevation: null,
                  color: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(24.0),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: TaskListWidget(selectedDate:_selectedDate, tasks: _tasksByDate),
                  ),
                ),
              ),
            ]),
      ),
    );
  }
}

class TaskForm extends StatefulWidget {
  final DateTime selectedDate;
  final void Function(Task task) addNewTask;
  TaskForm({required this.selectedDate, required this.addNewTask});
  @override
  _TaskFormState createState() => _TaskFormState();
}

class _TaskFormState extends State<TaskForm> {
  final TextEditingController _describtionController = TextEditingController();
  final TextEditingController _nameController = TextEditingController();
  final DateFormat _dateFormat = DateFormat('dd.MM.yyyy');
  bool _formValid = true;

  @override
  void dispose() {
    _describtionController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  void _handleAddButtonPressed() {
    if (_describtionController.text.isEmpty ||  _nameController.text.isEmpty) {
      setState(() {
        _formValid = false;
      });
    } else {
      setState(() {
        _formValid = true;
      });
      widget.addNewTask(Task(taskId: 0,name: _nameController.text, description: _describtionController.text, dueDate: widget.selectedDate));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Add new task',
          style: TextStyle(fontSize: 24.0, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 16.0),
        TextField(
          controller: _nameController,
          decoration: InputDecoration(
            hintText: 'Name',
            border:
                OutlineInputBorder(borderRadius: BorderRadius.circular(16.0)),
            filled: true,
            fillColor: Colors.grey[200],
            contentPadding:
                EdgeInsets.symmetric(vertical: 12.0, horizontal: 16.0),
            errorText: _nameController.text.isEmpty && !_formValid
                ? 'Name is required'
                : null,
          ),
        ),
        SizedBox(height: 16.0),
        TextField(
          readOnly: true,
          enabled: false,
          showCursor: false,
          decoration: InputDecoration(
            hintText: _dateFormat.format(widget.selectedDate),
            border:
                OutlineInputBorder(borderRadius: BorderRadius.circular(16.0)),
            filled: true,
            fillColor: Colors.grey[200],
            contentPadding:
                EdgeInsets.symmetric(vertical: 12.0, horizontal: 16.0)
          ),
        ),
        SizedBox(height:16),
          TextField(
          controller: _describtionController,
          decoration: InputDecoration(
            hintText: 'Description ...',
            border:
                OutlineInputBorder(borderRadius: BorderRadius.circular(16.0)),
            filled: true,
            fillColor: Colors.grey[200],
            contentPadding:
                EdgeInsets.symmetric(vertical: 12.0, horizontal: 16.0),
            errorText: _describtionController.text.isEmpty && !_formValid
                ? 'Description is required'
                : null,
          ),
        ),
        SizedBox(height: 16.0),
        TextButton(
          style: TextButton.styleFrom(
            padding: EdgeInsets.zero,
            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
          onPressed: _handleAddButtonPressed,
          child: Container(
            width: double.infinity,
            padding: EdgeInsets.symmetric(vertical: 10, horizontal: 20),
            decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16), // radius of 10
                color: Colors.deepPurpleAccent 
                ),
            child: Center(
              child: Text(
                'Add',
                style: TextStyle(color: Colors.white, fontSize: 20),
              ),
            ),
          ),
        )
      ],
    );
  }
}

class TaskListWidget extends StatefulWidget {
  final DateTime selectedDate;
  final List<Task> tasks;
  TaskListWidget({required this.selectedDate, required this.tasks});
  @override
  _TaskListWidgetState createState() => _TaskListWidgetState();
}

class _TaskListWidgetState extends State<TaskListWidget> {
  final DateFormat _dateFormat = DateFormat('EEE, dd MMMM');

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.only(bottom: 16.0),
          child: Text(
            _dateFormat.format(widget.selectedDate), 
            style: TextStyle(fontSize: 24.0, fontWeight: FontWeight.bold),
          ),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: widget.tasks.length,
            itemBuilder: (context, index) {
              return CheckboxListTile(
                title: Text(widget.tasks[index].name),
                value: widget.tasks[index].isDone,
                onChanged: (value) {
                  setState(() {
                    widget.tasks[index].isDone = value!;
                  });
                },
              );
            },
          ),
        ),
        Row(mainAxisAlignment: MainAxisAlignment.end, children: [
             TextButton(
          style: TextButton.styleFrom(
            padding: EdgeInsets.zero,
            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
          onPressed: () { /*TODO: delete tasks*/},
          child: Container(
            padding: EdgeInsets.symmetric(vertical: 10, horizontal: 20),
            decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16), // radius of 10
                color: Colors.deepPurpleAccent 
                ),
            child: Center(
              child: Text(
                'Done',
                style: TextStyle(color: Colors.white, fontSize: 20),
              ),
            ),
          ),
        )

        ],)
      ],
    );
  }
}
