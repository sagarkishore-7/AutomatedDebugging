from types import FrameType, TracebackType
from typing import Any, Optional, Type
from debuggingbook.PerformanceDebugger import HitCollector, PerformanceDebugger

class HitCollector(HitCollector):
    def __init__(self, limit: int = 100000) -> None:
        super().__init__()
        self.counter = limit

    def collect(self, frame: FrameType, event: str, arg: Any) -> None:
        if self.counter > 0:
            super().collect(frame, event, arg)
            self.counter -= 1
        else:
            raise OverflowError


class PerformanceDebugger(PerformanceDebugger):
    def is_overflow(self) -> bool:
        return self.collector.counter == 0

    def __exit__(self, exc_tp: Type, exc_value: BaseException, exc_traceback: TracebackType) -> Optional[bool]:
        outcome = self.PASS if exc_tp is None else self.FAIL if exc_tp == OverflowError else None
        if outcome is not None:
            self.add_collector(outcome, self.collector)
            return True
        return super().__exit__(exc_tp, exc_value, exc_traceback)


if __name__ == '__main__':
    def loop(x: int):
        x = x + 1
        while x > 0:
            pass

    with PerformanceDebugger(HitCollector) as debugger:
        loop(1)

    assert debugger.is_overflow()
    print(debugger)
