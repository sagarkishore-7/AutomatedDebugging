import logging
import os
import pickle
import shutil
import ast
from ast import NodeTransformer, AST
from pathlib import Path
from types import FrameType
from typing import List, Any, Set, Dict, Tuple

from debuggingbook.StatisticalDebugger import ContinuousSpectrumDebugger, Collector, RankingDebugger
from debuggingbook.Slicer import TrackCallTransformer, TrackControlTransformer, TrackParamsTransformer, TrackReturnTransformer, TrackGetTransformer, TrackSetTransformer
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
            # Create the same subdirectory in the destination directory

            des_directory = directory.replace(source_directory.__repr__(), dest_directory.__repr__(), 1)
            f_o_index = des_directory.find('\\')
            print(des_directory)
            ein_level = des_directory[f_o_index + 1:]
            print(ein_level)
            s_o_index = ein_level.find('\\')
            da_sub = ein_level[s_o_index:]
            new_des_directory = str(dest_directory) + da_sub
            os.makedirs(new_des_directory, exist_ok=True)
            # new_list = [string[string.find("\\") + 1:] for string in des_directory if "\\" in string]
            r_o_index = str(directory).rfind('\\')
            print('this is da_sub ', da_sub)
            print('this is dir ', directory)
            print('this is sub dir', sub_directories)
            print('this is src dir', source_directory)
            print('this is des dir', dest_directory)

            for file in files:
                print(file)
                print(da_sub)
                f_p = Path(directory, file)
                if f_p not in excluded_paths:
                    # Check if the file is a Python file
                    if file.endswith(".py"):
                        # print(da_sub)
                        # print(directory)
                        print(r_o_index, "this r")
                        print(f_o_index, 'this is f')
                        print(s_o_index, 'this is s')
                        if r_o_index == f_o_index or r_o_index == s_o_index:
                            print(file, 'we here')
                            with open(os.path.join(directory, file), "r") as src_file:
                                # print(src_file)
                                with open(os.path.join(Path(dest_directory), file), "w") as dst_file:
                                    # print(dst_file)
                                    print(dst_file)
                                    self.direct_write(src_file, dst_file)
                        else:
                            with open(os.path.join(directory, file), "r") as src_file:
                                with open(os.path.join(Path(new_des_directory), file), "w") as dst_file:
                                    print(dst_file, 'this dst')
                                    self.direct_write(src_file, dst_file)
                            # Open the file and add the print statement
                            # print(file)
                else:
                    if r_o_index == f_o_index or r_o_index == s_o_index:
                        with open(os.path.join(directory, file), "r") as src_file:
                            with open(os.path.join(Path(dest_directory), file), "w") as dst_file:
                                conn = src_file.read()
                                dst_file.write(conn)
                    else:
                        with open(os.path.join(directory, file), "r") as src_file:
                            with open(os.path.join(Path(new_des_directory), file), "w") as dst_file:
                                conn = src_file.read()
                                dst_file.write(conn)

            # Iterates directory and its subdirectories in the form of (directory, [sub_directories], [files])
            logging.info(f'Current dir: {directory}')
            logging.info(f'Current sub_dirs: {sub_directories}')
            logging.info(f'Current files: {files}')

        def direct_write(self, src, des):
            con = src.read()
            tr = ast.parse(con)
            n_tr = self.transform(tr)
            fin = ast.unparse(n_tr)
            des.write("from lib import _data \n")
            des.write(fin)

        def transformers(self) -> List[NodeTransformer]:
            """List of transformers to apply. To be extended in subclasses."""
            return [
                TrackCallTransformer(),
                TrackSetTransformer(),
                TrackGetTransformer(),
                TrackControlTransformer(),
                TrackReturnTransformer(),
                TrackParamsTransformer()
            ]

        def transform(self, tree: AST) -> AST:
            """Apply transformers on `tree`. May be extended in subclasses."""
            # Apply transformers
            for transformer in self.transformers():
                if self.log >= 3:
                    print(transformer.__class__.__name__ + ':')

                transformer.visit(tree)
                ast.fix_missing_locations(tree)
                if self.log >= 3:
                    print_content(ast.unparse(tree), '.py')
                    print()
                    print()

            if 0 < self.log < 3:
                print_content(ast.unparse(tree), '.py')
                print()
                print()

            return tree


class DependencyCollector(Collector):

    def __init__(self, dump_path: Path):
        super().__init__()
        self.dump_path = dump_path

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

    pass

    def events(self) -> Set[Any]:
        pass


class CoverageDependencyCollector(DependencyCollector):

    def events(self) -> Set[Any]:
        pass


class DependencyDebugger(ContinuousSpectrumDebugger, RankingDebugger):

    def __init__(self, coverage=False, log: bool = False):
        super().__init__(CoverageDependencyCollector if coverage else DependencyCollector, log)
