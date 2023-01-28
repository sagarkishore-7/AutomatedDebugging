import logging
import os
import pickle
import shutil
import ast
from ast import AST
from ast import NodeTransformer
from pathlib import Path
from types import FrameType
from typing import List, Any, Set, Dict, Tuple, Union

from debuggingbook.Slicer import TrackSetTransformer, TrackCallTransformer, TrackGetTransformer, \
    TrackControlTransformer, TrackReturnTransformer, TrackParamsTransformer
from debuggingbook.StatisticalDebugger import ContinuousSpectrumDebugger, Collector, RankingDebugger
from debuggingbook.bookutils import print_content

DependencyDict = Dict[
    str,
    Set[
        Tuple[
            Tuple[str, Tuple[str, int]],
            Tuple[Tuple[str, Tuple[str, int]], ...]
        ]
    ]
]


class Instrumenter(NodeTransformer):

    def instrument(self, source_directory: Path, dest_directory: Path, excluded_paths: List[Path], log=False) -> None:
        """
        TODO: implement this function, such that you get an input directory, instrument all python files that are
        TODO: in the source_directory whose prefix are not in excluded files and write them to the dest_directory.
        TODO: keep in mind that you need to copy the structure of the source directory.
        :param source_directory: the source directory where the files to instrument are located
        :param dest_directory:   the output directory to which to write the instrumented files
        :param excluded_paths:   the excluded path that should be skipped in the instrumentation
        :param log:              whether to log or not
        :return:
        """

        if log:
            logging.basicConfig(level=logging.INFO)

        assert source_directory.is_dir()

        if dest_directory.exists():
            shutil.rmtree(dest_directory)
        os.makedirs(dest_directory)

        shutil.copy('lib.py', dest_directory / 'lib.py')

        for directory, sub_directories, files in os.walk(source_directory):
            # Iterates directory and its subdirectories in the form of (directory, [sub_directories], [files])
            logging.info(f'Current dir: {directory}')
            logging.info(f'Current sub_dirs: {sub_directories}')
            logging.info(f'Current files: {files}')
            for file in files:
                """Check if file included in excluded path list"""
                if Path(directory, file) not in excluded_paths:
                    """Read file ending with .py from source directory"""
                    if file.endswith('.py'):
                        with open(Path(directory, file), 'r') as f:
                            file_contents = f.read()
                            """Parse the code into AST"""
                            file_tree = ast.parse(file_contents)
                            """Create a new AST node for the import and add it to the top of the body"""
                            new_node = ast.ImportFrom(module='lib', names=[ast.alias(name='_data', asname=None)], level=0)
                            file_tree.body.insert(0, new_node)
                            """Modification to the code using visit method"""
                            TrackCallTransformer().visit(file_tree)
                            TrackSetTransformer().visit(file_tree)
                            TrackGetTransformer().visit(file_tree)
                            TrackControlTransformer().visit(file_tree)
                            TrackReturnTransformer().visit(file_tree)
                            TrackParamsTransformer().visit(file_tree)

                            """Write the modified code to source directory"""
                            destination_directory = Path(dest_directory, Path(directory, file).relative_to(source_directory))
                            os.makedirs(destination_directory.parent, exist_ok=True)
                            with open(destination_directory, 'w') as f:
                                source_code = ast.unparse(file_tree)
                                f.write(source_code)
                else:
                    """Copy the file to destination directory from temp"""
                    destination_directory = Path(dest_directory, Path(directory, file).relative_to(source_directory))
                    os.makedirs(destination_directory.parent, exist_ok=True)
                    shutil.copy(Path(directory, file), destination_directory)

class DependencyCollector(Collector):

    def __init__(self, dump_path: Path):
        super().__init__()
        self.dump_path = dump_path
        self.deps = list()

    def traceit(self, frame: FrameType, event: str, arg: Any) -> None:
        pass  # deactivate tracing overall, not required.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.dump_path, 'rb') as dump:
            deps = pickle.load(dump)
        self.collect(deps)

    def collect(self, dependencies: DependencyDict):
        """
        TODO: Collect the dependencies in the specified format.
        :param dependencies: The dependencies for a run
        :return:
        """
        control_dependencies = dependencies.get('control')
        data_depepdencies = dependencies.get('data')
        for dep in control_dependencies:
            self.deps.append(dep)
        for dep in data_depepdencies:
            self.deps.append(dep)

    def events(self) -> Set[Any]:
        return set(self.deps)


class CoverageDependencyCollector(DependencyCollector):

    def events(self) -> Set[Any]:
        event_line = list()
        deps = super().events()
        for dep in deps:
            event_line.append(dep[0][1])
        return set(event_line)


class DependencyDebugger(ContinuousSpectrumDebugger, RankingDebugger):

    def __init__(self, coverage=False, log: bool = False):
        super().__init__(CoverageDependencyCollector if coverage else DependencyCollector, log)
