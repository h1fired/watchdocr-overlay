from src.common.api import KernelAPI
from src.watchdocr.workflow import WatchdOcrWorkflow, WatchdOcrWorkflowManager


class WorkflowAPI(KernelAPI):
    def __init__(self, kernel):
        super().__init__(kernel)
        self._manager: WatchdOcrWorkflowManager = self.kernel.objects.pull('watchdocr-workflows')

    def switch_to(self, workflow: type[WatchdOcrWorkflow]):
        self._manager.switch_to(workflow)

    def provide_context_data(self, data: dict):
        workflow = self._manager.get_current_workflow()
        workflow.provide_context_data(data)

    def execute(self):
        workflow = self._manager.get_current_workflow()
        workflow.execute()
