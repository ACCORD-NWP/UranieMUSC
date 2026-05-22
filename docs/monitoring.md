# Monitoring the Pipeline

UranieMUSC can run entirely from the command line without any extra infrastructure. However, Luigi also provides a **web-based dashboard** that shows the status of every task in real time — useful for longer runs where you want to track progress without staring at log output.

This page explains how to start the Luigi scheduler on ATOS and access the dashboard from your local machine.

---

## Option A: Local scheduler (no web UI)

The simplest approach. Add `--local-scheduler` to any task command:

```shell
uv run uranmusc Run --local-scheduler
```

Luigi manages the pipeline internally and prints status to the terminal. No server setup is needed.

---

## Option B: Luigi scheduler server (with web UI)

### 1. Start the Luigi scheduler on ATOS

Open a terminal on ATOS (or inside a `screen`/`tmux` session so it survives disconnects) and run:

```shell
uv run --active luigid --address 127.0.0.1 --port 8082
```

This starts the Luigi central scheduler, listening on `localhost:8082`. Keep this terminal open for the duration of your run.

### 2. Run the pipeline pointing at the scheduler

In a separate terminal, run your tasks with `--scheduler-port` instead of `--local-scheduler`:

```shell
uv run uranmusc Run --scheduler-port 8082
```

Luigi will connect to the scheduler and register all tasks with it.

### 3. Port-forward to your local machine

The ATOS login node (`hpc-login`) is not directly accessible from a browser on your laptop. Use SSH port-forwarding to bridge the connection. On your **local machine**, run:

```shell
ssh -L 8080:127.0.0.1:8082 hpc-login
```

This forwards your local port 8080 to port 8082 on the ATOS login node.

### 4. Open the dashboard

Navigate to `http://127.0.0.1:8080/` in your local browser.

---

## Reading the Luigi dashboard

The dashboard has two main views:

### Task graph

Shows the dependency graph of all registered tasks. Each node is coloured by status:

| Colour | Meaning |
|---|---|
| Grey | Pending — waiting for dependencies |
| Yellow | Running |
| Green | Complete (outputs exist) |
| Red | Failed |
| Blue | Disabled / skipped |

Click on a task node to see its parameters, start time, and worker assignment.

### Task list

A searchable table of all tasks with their current status and last update time. Useful for quickly finding a failing task in a large run.

---

## Viewing logs

Luigi writes a timestamped log file to `logs/` in the repository directory. The filename is formatted as `logs/YYYYMMDDTHHMMSS.log`. To follow the log in real time:

```shell
tail -f logs/<timestamp>.log
```

---

## Troubleshooting

**The dashboard is empty / tasks are not appearing**

Make sure you are using `--scheduler-port 8082` and not `--local-scheduler` when running tasks. Tasks run with `--local-scheduler` are not registered with the central scheduler.

**Port-forward connection refused**

Check that `luigid` is still running on ATOS. If it crashed or the session closed, restart it and re-establish the port-forward.

**`Address already in use` when starting `luigid`**

Another `luigid` process is already running on port 8082. Either kill it (`pkill luigid`) or choose a different port (remember to update both the `luigid` command and the `--scheduler-port` argument).
