"""ParallelFFmpeg Tests."""
from time import sleep
from unittest import mock

import pytest

from m4b_util.helpers.parallel_ffmpeg import ParallelFFmpeg


@pytest.fixture()
@mock.patch("m4b_util.helpers.parallel_ffmpeg.Progress")
def processor(progress):
    """Set up the processor and mock out the progress tracker."""
    p = ParallelFFmpeg("Testing")
    p._tasklist.append({  # noqa
        "name": "Master",
        "task_id": 0
    })
    p._tasklist.append({  # noqa
        "name": "Frist",
        "task_id": None
    })

    return p, progress()


def _add_to_q(q, message):
    """Add message to queue, and wait until the queue is not empty."""
    q.put(message)
    while q.empty():
        sleep(0.25)  # Give time for the queue to populate


def test_read_status_q_empty(processor):
    """Read an empty queue idempotently."""
    p, progress = processor
    p._read_status_queue()  # Should be a no-op, since queue is empty
    assert p._tasklist[1]["task_id"] is None
    progress.update.assert_not_called()


def test_read_status_q_new(processor):
    """Read a new task event."""
    # Set things up
    p, progress = processor
    progress.add_task = mock.MagicMock(return_value=333)
    _add_to_q(p._status_q, (1, "started"))

    # Test it!
    p._read_status_queue()
    assert p._tasklist[1]["task_id"] == 333
    progress.add_task.assert_called()
    progress.update.assert_not_called()


def test_read_status_q_update(processor):
    """Read a progress update."""
    p, progress = processor
    p._tasklist[1]["task_id"] = 24

    # 50% complete
    _add_to_q(p._status_q, (1, 50))
    p._read_status_queue()
    progress.update.assert_called_with(24, completed=50)

    # 100% Complete
    _add_to_q(p._status_q, (1, 100))
    p._read_status_queue()
    progress.update.assert_called_with(24, completed=100)


def test_read_status_finished(processor):
    """Read a task finished event."""
    p, progress = processor
    p._tasklist[1]["task_id"] = 48

    _add_to_q(p._status_q, (1, "finished"))
    p._read_status_queue()
    progress.update.assert_has_calls([
        mock.call(48, completed=100, visible=False),  # Specified Task
        mock.call(0, advance=1)  # Master Task
    ])


def test_read_status_failed(processor):
    """Read a task failed event."""
    p, progress = processor
    p._tasklist[1]["task_id"] = 12

    _add_to_q(p._status_q, (1, "failed"))
    p._read_status_queue()
    progress.console.print.assert_called_with("[red]Error:[/] Failed to process Frist")
    progress.update.assert_has_calls([
        mock.call(12, visible=False),  # Specified Task
        mock.call(0, advance=1)  # Master Task
    ])


@mock.patch("m4b_util.helpers.parallel_ffmpeg.FFProgress")
def test_ffmpeg_job(ff, processor):
    """Run a single worker job."""
    # Mock out the run command so we don't have to be dependent on system configurations.
    ff().run.return_value = [0, 50, 100]
    p, _ = processor
    status_q = mock.MagicMock()

    # Add jobs
    p._input_q.put((60, ["should-pass"]))
    p._input_q.put((72, ["should-pass"]))
    p._input_q.put(None)  # Shuts down worker

    # Process the job
    p._ffmpeg_job(p._input_q, status_q)
    status_q.put.assert_has_calls([
        mock.call((60, "started")),
        mock.call((60, 0)),
        mock.call((60, 50)),
        mock.call((60, 100)),
        mock.call((60, "finished")),
        mock.call((72, "started")),
        mock.call((72, 0)),
        mock.call((72, 50)),
        mock.call((72, 100)),
        mock.call((72, "finished"))
    ])


@mock.patch("m4b_util.helpers.parallel_ffmpeg.FFProgress")
def test_ffmpeg_job_fail(ff, processor):
    """Run a single worker job, with a failing task."""
    # Mock out the run command so we don't have to be dependent on system configurations.
    def ffrun():
        raise RuntimeError("FAIL!")
    ff().run.side_effect = ffrun
    p, _ = processor
    status_q = mock.MagicMock()

    # Add jobs
    p._input_q.put((84, ["should-fail"]))
    p._input_q.put(None)  # Shuts down worker

    # Process the job
    p._ffmpeg_job(p._input_q, status_q)
    status_q.put.assert_has_calls([
        mock.call((84, "started")),
        mock.call((84, "failed")),
    ])


def test_process_empty_tasklist(processor):
    """Return none if task arg is empty."""
    p, _ = processor
    assert p.process(list()) is None


@mock.patch("m4b_util.helpers.parallel_ffmpeg.Progress")
def test_process(progress):
    """Run a multiprocess job."""
    p = ParallelFFmpeg("Testing")

    # Create tasklist.
    # Because _ffmpeg_job will be run in separate processes, we can't mock out FFProgress. This means we do, actually,
    # need a real command.
    tasks = list()
    for i in range(25):
        tasks.append({
            "name": str(i),
            "command": ["ffprobe", "-version"]
        })

    # Process the job.
    # We can't check anything that happens in _ffmpeg_job because it is run in a separate process.
    assert p.process(tasks)
    progress().start.assert_called()
    progress().add_task.assert_has_calls([
        mock.call("[cyan]Testing", total=25)
    ])
    progress().stop.assert_called()


@mock.patch("m4b_util.helpers.parallel_ffmpeg.Progress")
def test_process_crashing_tasks(progress):
    """Run a job with tasks that crash.

    In a previous version, crashing tasks, or too few tasks would lead to an infinite loop.
    """
    p = ParallelFFmpeg("Testing")

    # Create tasklist.
    tasks = list()
    for i in range(2):
        tasks.append({
            "name": str(i),
            "command": ["not-a-command"]
        })

    # Process the job.
    assert p.process(tasks)
    progress().start.assert_called()
    progress().add_task.assert_has_calls([
        mock.call("[cyan]Testing", total=2)
    ])
    progress().stop.assert_called()
