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

    def is_active(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def provide_context_data(self, data: dict):
        if not self.is_active():
            raise RuntimeError('Cannot provide context data while manager is inactive')

        self._processor.queue_pipeline(
            strategy=PipelineStrategy.ONLY_CONTEXT_CHANGE,
            context_data=data
        )


class WatchdOcrWorkflowManager:
    def __init__(self, workflows: tuple[WatchdOcrWorkflow, ...]):
        self._workflows = {type(w): w for w in workflows}
        self._current: WatchdOcrWorkflow | None = None
        self._active = False

    def start(self):
        if self._active:
            return
        if self._current:
            self._current.run()
        self._active = True

    def stop(self):
        if not self._active:
            return
        if self._current:
            self._current.close()
        self._active = False

    def is_active(self):
        return self._active

    def switch_to(self, workflow: type[WatchdOcrWorkflow]):
        if workflow not in self._workflows.keys():
            raise TypeError(f'Invalid workflow type -> {type(workflow)}')

        if workflow is type(self._current):
            return

        if self._current:
            log.info('Closing current workflow: %s', self._current.__class__.__name__, extra={'title': 'Workflow'})
            self._current.close()

        new = self._workflows[workflow]
        log.info('Switching to workflow: %s', new.__class__.__name__, extra={'title': 'Workflow'})

        if self._active:
            new.run()

        self._current = new

    def get_current_workflow(self):
        return self._current
