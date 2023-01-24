from types import FrameType, TracebackType
from typing import Any, Optional, Type
from debuggingbook.PerformanceDebugger import HitCollector, PerformanceDebugger

class HitCollector(HitCollector):
    def __init__(self, limit: int = 100000) -> None:
        super().__init__()
        pass # YOUR CODE HERE

    def collect(self, frame: FrameType, event: str, arg: Any) -> None:
        pass # YOUR CODE HERE

    pass # OTHER CODE if necessary

class PerformanceDebugger(PerformanceDebugger):
    def is_overflow(self) -> bool:
        pass # YOUR CODE HERE

    def __exit__(self, exc_tp: Type, exc_value: BaseException, exc_traceback: TracebackType) -> Optional[bool]:
        pass # YOUR CODE HERE

    pass # OTHER CODE if necessary


if __name__ == '__main__':
    def loop(x: int):
        x = x + 1
        while x > 0:
            pass

    with PerformanceDebugger(HitCollector) as debugger:
        loop(1)

    assert debugger.is_overflow()
    print(debugger)
