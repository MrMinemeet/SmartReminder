class Task:
    def __init__(self, taskId, name, description, personName, date):
        self.taskId = taskId
        self.name = name
        self.description = description
        self.personName = personName
        self.date = date

    def __str__(self):
        return f"{self.taskId} {self.name} {self.description} {self.personName} {self.date}"

    def to_json(self):
        return {
            'taskId': self.taskId,
            'name': self.name,
            'description': self.description,
            'personId': self.personName,
            'dueDate': self.date
        }
