from src.watchdocr.processor.context import RuntimeConfig
from src.watchdocr.workflow import WatchdOcrWorkflowManager
from src.watchdocr.workflow.live import LiveWorkflow
from src.watchdocr.workflow.onetime import OnetimeWorkflow
from types import SimpleNamespace
import src.watchdocr.workflow.live as live_module
import asyncio
import pytest


class FakeProcessor:
    def __init__(self, boundings=(0, 0, 10, 10), block=False):
        self._config = RuntimeConfig(boundings=boundings)
        self.block = block
        self.tasks = []
        self.skip_flags = []

    def config(self):
        return self._config

    def queue_pipeline(self, strategy, context_data, skip_unchanged=False):
        self.skip_flags.append(skip_unchanged)
        if self.block:
            coro = asyncio.Event().wait()
        else:
            coro = asyncio.sleep(0)
        task = asyncio.create_task(coro)
        self.tasks.append(task)
        return task


@pytest.fixture(autouse=True)
def fast_live_mode(monkeypatch):
    # Real settings object would save every change to the user's file
    monkeypatch.setattr(
        live_module, 'settings',
        SimpleNamespace(live_mode_recognition_frequency=0.001)
    )


async def test_live_workflow_runs_pipelines_periodically():
    processor = FakeProcessor()
    workflow = LiveWorkflow(processor)

    await workflow.run()
    await asyncio.sleep(0.05)
    await workflow.close()

    assert len(processor.tasks) >= 2
    assert not workflow.is_active()
    # First result is always sent, next unchanged ones are skipped
    assert processor.skip_flags[0] is False
    assert all(processor.skip_flags[1:])


async def test_live_workflow_skips_empty_boundings():
    processor = FakeProcessor(boundings=(0, 0, 0, 0))
    workflow = LiveWorkflow(processor)

    await workflow.run()
    await asyncio.sleep(0.02)
    await workflow.close()

    assert processor.tasks == []


async def test_live_workflow_close_cancels_running_pipeline():
    processor = FakeProcessor(block=True)
    workflow = LiveWorkflow(processor)

    await workflow.run()
    await asyncio.sleep(0.01)
    await workflow.close()
    await asyncio.wait(processor.tasks)

    assert len(processor.tasks) == 1
    assert processor.tasks[0].cancelled()


async def test_manager_switch_closes_previous_workflow():
    processor = FakeProcessor(block=True)
    onetime = OnetimeWorkflow(processor)
    live = LiveWorkflow(processor)
    manager = WatchdOcrWorkflowManager(workflows=(onetime, live))

    await manager.switch_to(LiveWorkflow)
    await manager.start()
    assert live.is_active()

    await manager.switch_to(OnetimeWorkflow)
    assert not live.is_active()
    assert onetime.is_active()

    await manager.stop()
    assert not onetime.is_active()
    assert not manager.is_active()


async def test_manager_concurrent_start_stop_are_serialized():
    processor = FakeProcessor(block=True)
    live = LiveWorkflow(processor)
    manager = WatchdOcrWorkflowManager(workflows=(live,))
    await manager.switch_to(LiveWorkflow)

    await asyncio.gather(manager.start(), manager.stop(), manager.start())

    assert manager.is_active()
    assert live.is_active()
    await manager.stop()
