from src.common.api import KernelAPI
from src.watchdocr.workflow import WatchdOcrWorkflow, WatchdOcrWorkflowManager


class WorkflowAPI(KernelAPI):
    def __init__(self, kernel):
        super().__init__(kernel)
        self._manager: WatchdOcrWorkflowManager = self.kernel.objects.pull('watchdocr-workflows')

    def start(self):
        self._manager.start()

    def stop(self):
        self._manager.stop()

    def is_active(self):
        return self._manager.is_active()

    def switch_to(self, workflow: type[WatchdOcrWorkflow] | None):
        self._manager.switch_to(workflow)

    def provide_context_data(self, data: dict):
        workflow = self._manager.get_current_workflow()
        workflow.provide_context_data(data)

    def execute(self):
        workflow = self._manager.get_current_workflow()
        workflow.execute()

    def get_current_workflow_type(self):
        return type(self._manager.get_current_workflow())
