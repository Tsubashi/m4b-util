"""Handle processsing audio files in parallel."""
import multiprocessing as mp
import os
import queue

from rich.progress import Progress, SpinnerColumn

from .ffprogress import FFProgress


class ParallelFFmpeg:
    """Process audio files in parallel."""

    def __init__(self, purpose):
        """Initialize everything.

        :param purpose: Description of overall purpose. Printed in front of the overall progress bar.
        """
        # Store our parameters
        self._purpose = purpose

        # Set up our member variables
        num_cores = os.cpu_count()
        self._input_q = mp.Queue(maxsize=num_cores)
        self._status_q = mp.Queue(maxsize=100)
        self._tasklist = list()
        self.temp_files = list()

        # Progress Tracker
        self.progress = Progress(SpinnerColumn(), *Progress.get_default_columns())

    def _read_status_queue(self):
        """Read info from the status queue and update the display."""
        try:
            master_task = self._tasklist[0]["task_id"]
            (job_id, job_status) = self._status_q.get_nowait()
            task_name = self._tasklist[job_id]["name"]
            if job_status == "started":
                self._tasklist[job_id]["task_id"] = self.progress.add_task(
                    f"[dark_cyan]|- Processing '[white]{task_name}[/]'.",
                    total=100
                )
            elif job_status == "finished":
                self.progress.update(self._tasklist[job_id]["task_id"], completed=100, visible=False)
                self.progress.update(master_task, advance=1)
            elif job_status == "failed":
                name = self._tasklist[job_id]["name"]
                self.progress.console.print(f"[red]Error:[/] Failed to process {name}")
                self.progress.update(self._tasklist[job_id]["task_id"], visible=False)
                self.progress.update(master_task, advance=1)
            else:  # No matching text means it is an update on percentage.
                self.progress.update(self._tasklist[job_id]["task_id"], completed=job_status)
        except queue.Empty:
            pass  # We don't actually care if the finished queue is empty

    def _insert_into_input_q(self, args):
        while True:
            # Check the status
            self._read_status_queue()
            # See if there is space in the queue
            try:
                self._input_q.put_nowait(args)
                break  # No need to keep looping once we have successfully written the queue
            except queue.Full:
                pass  # We will just try again.

    @staticmethod
    def _ffmpeg_job(q, status_q):
        """Multiprocessing worker that runs an ffmpeg command."""
        while True:
            args = q.get()
            if args is None:
                break

            (job_id, cmd) = args

            # Let the outside world know we started
            status_q.put((job_id, "started"))

            try:
                ff = FFProgress(cmd)
                for percent in ff.run():
                    status_q.put((job_id, percent))
                status_q.put((job_id, "finished"))
            # Since we need these workers to stay up until we close them, we will catch all but the most
            # dire exceptions.
            except Exception as e:  # noqa: See comment above.
                status_q.put((job_id, "failed"))
                continue

    def process(self, tasks):
        """Use multiprocessing to run all ffmpeg commands.

        :param tasks: A list of dictionaries with two keys: 'name' and 'command'. Name will be printed by the progress
                      tracker while command is being run.
        """
        # Make sure we have tasks
        if len(tasks) == 0:
            return None

        # Start up our progress tracker
        self.progress.start()

        # Set up our processing pool
        num_cores = os.cpu_count()
        pool = mp.Pool(num_cores, initializer=self._ffmpeg_job, initargs=(self._input_q, self._status_q))

        master_task = self.progress.add_task(
            f"[cyan]{self._purpose}",
            total=len(tasks)
        )
        self._tasklist.append({
            "name": "Master",
            "task_id": master_task
        })

        for task in tasks:
            # Mark a new task as beginning.
            self._tasklist.append({
                "name": task.get("name", "unknown"),
                "task_id": None
            })
            job_id = len(self._tasklist) - 1

            # Send the info to our workers
            args = (job_id, task["command"])
            self._insert_into_input_q(args)

        # Tell the workers we are all done
        for _ in range(num_cores):
            self._insert_into_input_q(None)
        pool.close()

        # Wait for all the jobs to finish
        while not (self._input_q.empty() and self._status_q.empty()):
            self._read_status_queue()
        pool.join()

        # Make sure the master task shows as completed
        # Yes, we need to doublecheck the status_q again, because the process of verifying the status_q is empty
        # and joining the pool is not atomic.
        while not self._status_q.empty():
            self._read_status_queue()  # nocover: This is just a timing thing, and can't be tested reliably.
        self.progress.update(master_task, completed=len(tasks))

        # Shut down the progress tracker
        self.progress.stop()

        return True
