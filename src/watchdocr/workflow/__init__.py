from src.watchdocr.processor.processor import (
    WatchdOcrProcessor,
    PipelineStrategy
)


class WatchdOcrWorkflow:
    def __init__(self, processor: WatchdOcrProcessor):
        self._processor = processor

    def run(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def provide_context_data(self, data: dict):
        self._processor.queue_pipeline(
            strategy=PipelineStrategy.ONLY_CONTEXT_CHANGE,
            context_data=data
        )


class WatchdOcrWorkflowManager:
    def __init__(self, workflows: tuple[WatchdOcrWorkflow, ...]):
        self._workflows = {type(w): w for w in workflows}
        self._current: WatchdOcrWorkflow | None = None

    def switch_to(self, workflow: type[WatchdOcrWorkflow] | None):
        if workflow is type(self._current):
            return

        if self._current:
            self._current.close()

        if workflow is None:
            self._current = None
            return

        new = self._workflows[workflow]
        new.run()
        self._current = new

    def get_current_workflow(self):
        return self._current
