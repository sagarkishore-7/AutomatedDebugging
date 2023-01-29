import logging
import os
import pickle
import shutil
import ast
from ast import NodeTransformer, AST
from pathlib import Path
from types import FrameType
from typing import List, Any, Set, Optional, Union

from debuggingbook.Slicer import TrackCallTransformer, TrackGetTransformer, TrackControlTransformer, \
    TrackReturnTransformer, TrackParamsTransformer, TrackSetTransformer
from debuggingbook.StatisticalDebugger import ContinuousSpectrumDebugger, Collector, RankingDebugger
from debuggingbook.bookutils import print_content


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
                            new_node = ast.ImportFrom(module='lib_fl', names=[ast.alias(name='data', asname=None)], level=0)
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

class EventCollector(Collector):

    def __init__(self, dump_path: Path):
        super().__init__()
        self.dump_path = dump_path
        self.deps = list()
        self.unique_set = set()

    def traceit(self, frame: FrameType, event: str, arg: Any) -> None:
        pass  # deactivate tracing overall, not required.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.dump_path, 'rb') as dump:
            events = pickle.load(dump)
        self.collect(events)

    def collect(self, dependencies: Any):
        control_dep = dependencies.get('control')
        data_dep = dependencies.get('data')

        for dep in control_dep:
            self.deps.append(dep)
        for dep in data_dep:
            self.deps.append(dep)

    def events(self) -> Set[Any]:
        name_and_line = list()
        deps = set(self.deps)
        for dep in deps:
            self.flatten_tuples(list(dep))
        return set(self.unique_set)

    def flatten_tuples(self, tup: list):
        flat_list: set = set()
        for x in tup:
            if type(x) == tuple:
                self.flatten_tuples(x)
            elif type(x) == str and type(tup[tup.index(x) + 1]) == int:
                new_tuple = (x, tup[tup.index(x) + 1])
                if new_tuple not in self.unique_set:
                    flat_list.add(new_tuple)
                    self.unique_set.add(new_tuple)

class FaultLocalization(ContinuousSpectrumDebugger, RankingDebugger):

    def __init__(self, instrumenter: Instrumenter, log: bool = False):
        ContinuousSpectrumDebugger.__init__(self, collector_class=EventCollector, log=log)
        RankingDebugger.__init__(self, collector_class=EventCollector, log=log)

    def rank(self) -> List[tuple[str, int]]:
        def susp(event: Any) -> float:
            suspiciousness = self.suspiciousness(event)
            assert suspiciousness is not None
            return suspiciousness

        events = list(self.all_events())
        events.sort(key=susp, reverse=True)
        events = self.mapping(events)
        return events

    def mapping(self, events: List):

        new_to_old_middle = {2: 1, 6: 2, 8: 3, 10: 4, 13: 5, 15: 6, 16: 7, 18: 8, 20: 9, 23: 10, 25: 11, 26: 12}
        new_to_old_remove_html_markup = {2: 1, 4: 2, 5: 3, 6: 4, 7: 6, 8: 7, 10: 8, 13: 9, 15: 10, 18: 11, 20: 12,
                                         23: 13, 25: 14, 26: 16}
        new_to_old_sqrt = {2: 1, 4: 2, 5: 3, 6: 4, 8: 5, 9: 6, 10: 8}
        new_to_old_interpreter = {2: 1, 3: 2, 5: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10, 13: 11, 15: 12,
                                         17: 13, 18: 14, 21: 15, 23: 16, 24: 17, 27: 18, 29: 19, 30: 20,
                                         33: 21, 35: 22, 36: 23, 39: 24, 41: 25, 42: 26, 45: 27, 47: 28,
                                         48: 29, 49: 30, 51: 31, 52: 32}
        new_to_old_parser = {2: 1, 3: 2, 5: 5, 7: 6, 8: 7, 9: 8, 11: 9, 14: 10, 16: 11, 19: 12,
                                         21: 13, 24: 14, 26: 15, 29: 16, 31: 17, 34: 18, 36: 19, 37: 20, 39: 21, 40: 22}
        new_events = []
        for e in events:
            # Convert tuple to list
            new_event_list = list(e)
            new_events.append(new_event_list)
        for e in new_events:
            if e[0] == 'middle':
                e[1] = new_to_old_middle.get(e[1])
            if e[0] == 'remove_html_markup':
                e[1] = new_to_old_remove_html_markup.get(e[1])
            if e[0] == 'sqrt':
                e[1] = new_to_old_sqrt.get(e[1])
            if e[0] == 'interpreter':
                e[1] = new_to_old_interpreter.get(e[1])
            if e[0] == 'parser':
                e[1] = new_to_old_parser.get(e[1])
        final_events = list()
        for e in new_events:
            updated_tuple = tuple(e)
            final_events.append(updated_tuple)
        return final_events