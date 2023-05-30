class Task:
    def __init__(self, taskId, name, description, personId, date):
        self.taskId = taskId
        self.name = name
        self.description = description
        self.personId = personId
        self.date = date

    def __str__(self):
        return f"{self.taskId} {self.name} {self.description} {self.personId} {self.date}"

    def to_json(self):
        return {
            'taskId': self.taskId,
            'name': self.name,
            'description': self.description,
            'personId': self.personId,
            'dueDate': self.date
        }
