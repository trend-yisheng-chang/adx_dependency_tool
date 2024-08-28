import uuid


class GraphNode():
    def __init__(self, title, content, type):
        self.id = str(uuid.uuid4())
        self.title = title
        self.content = content
        self.type = type

    def __eq__(self, other):
        if isinstance(other, GraphNode):
            return self.title == other.title and self.content == other.content and self.type == other.type
        return False

    def __hash__(self):
        return hash((self.title, self.content, self.type))
