import json
from unittest.mock import patch, call
from cli.hub.component import Component
from .test_generic import SplightHubTest
from ..settings import *
import subprocess

class TestInitialize(SplightHubTest):
    
    def test_initialize(self):
        self.component = Component(self.path)
        initialization_file_path = os.path.join(self.path, INIT_FILE)
        lines = []

        with open(initialization_file_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                lines.append(line)

        run_commands = [" ".join(line.split(" ")[1:]) for line in lines if line.startswith("RUN")]

        with patch.object(subprocess, "run") as runs:
            self.component.initialize()
            commands = run_commands
            calls = []
            for command in commands:
                calls.append(call(command, check=True, cwd=self.path, shell=True))
            runs.assert_has_calls(calls)
        
            
                


        
