from src.watchdocr.processor.processor import (
    WatchdOcrProcessor,
    PipelineStrategy
)
from src.common.utils.logging import log


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
            log.info('Closing current workflow: %s', self._current.__class__.__name__, extra={'title': 'Workflow'})
            self._current.close()

        if workflow is None:
            self._current = None
            log.info('Workflow manager disabled (no active workflow)', extra={'title': 'Workflow'})
            return

        new = self._workflows[workflow]
        log.info('Switching to workflow: %s', new.__class__.__name__, extra={'title': 'Workflow'})
        new.run()
        self._current = new

    def get_current_workflow(self):
        return self._current
