class Task:
    def __init__(self, taskId, name, description, personName, date):
        self.taskId = taskId
        self.name = name
        self.description = description
        self.personName = personName
        self.date = date
        self.state = False

    def __str__(self):
        return f"{self.taskId} {self.name} {self.description} {self.personName} {self.date} {self.state}"

    def to_json(self):
        return {
            'taskId': self.taskId,
            'name': self.name,
            'description': self.description,
            'personName': self.personName,
            'dueDate': self.date,
            'state': self.state
        }
