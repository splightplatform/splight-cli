class ComponentDirectoryAlreadyExists(Exception):
   def __init__(self, dir: str):
        super().__init__(f"Directory with name {dir} already exists in path")


class ComponentAlreadyExistsException(Exception):
    def __init__(self, component: str):
        super().__init__(f"Component with name {component} already exists in hub")

