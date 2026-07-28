import asyncio
from io import StringIO
from pathlib import Path

from IPython import display

DONE_MARKER = "[SBATCH-DONE]"

# ensure_future only keeps a weak reference, so a running job can be collected
# mid-flight unless we hold on to it here.
_TASKS = set()


class IWriter:
    "Class that sets up a live output display cell. .add(msg) will append to output."

    WATCH_COUNT = 1

    def __init__(self, msg):
        self.io = StringIO()
        self.io.write(msg)
        self.handle = display.display(
            {"text/plain": self.io.getvalue()},
            raw=True,
            display_id=self.__class__.WATCH_COUNT,
        )
        self.__class__.WATCH_COUNT += 1

    def add(self, msg):
        self.io.write(msg)
        self.handle.update({"text/plain": self.io.getvalue()}, raw=True)


async def submit_file(name, writer):
    "Submit a file, print the submission message and return the final item (the job number)"
    proc = await asyncio.create_subprocess_exec(
        "sbatch",
        f"--job-name={name}",
        f"--output={name}.out",
        f"{name}.sbatch",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()
    stdout = stdout.decode()

    writer.add(stdout)
    if "Submitted batch job " not in stdout:
        writer.add(stderr.decode())
        raise RuntimeError("Invalid job submission output")
    return stdout.split()[-1]


async def watch_file(filename, writer):
    "Watch a file, print live output, and exit when final argument seen."
    writer.add(f"Waiting for {filename}...\n")

    filename = Path(filename)
    while not filename.exists():
        await asyncio.sleep(0.5)
    # Blocking, but these are single short lines from a local file.
    with filename.open() as f:  # noqa: ASYNC230
        while True:
            r = f.readline()
            if DONE_MARKER in r:
                break
            elif r == "":
                await asyncio.sleep(0.5)
            else:
                writer.add(r)

    writer.add("Done!")


async def submit_and_watch(name):
    "Run submit and watch jobs"

    writer = IWriter(f"Submitting {name}.sbatch\n")

    sbatch = Path(f"{name}.sbatch")
    out = Path(f"{name}.out")

    out.unlink(missing_ok=True)

    await submit_file(name, writer)
    await watch_file(out, writer)

    out.unlink(missing_ok=True)
    sbatch.unlink(missing_ok=True)


def sbatch(line, cell):
    "Submit a job by name"
    (name,) = line.split()  # Name required
    assert "." not in name, "Do not include extension!"

    txt = cell.format(name=name, **globals()) + f'echo\necho "{DONE_MARKER}"\n'

    Path(f"{name}.sbatch").write_text(txt)

    task = asyncio.ensure_future(submit_and_watch(name))
    _TASKS.add(task)
    task.add_done_callback(_TASKS.discard)


def load_ipython_extension(ipython):
    ipython.register_magic_function(sbatch, magic_kind="cell")
