import random
import matplotlib.pyplot as plt

# Constants
NUM_TEAM_MEMBERS = 10  # Number of team members
NUM_PROJECTS = 10     # Number of projects
MAX_TASK_DURATION = 72  # Max duration for a task
MIN_TASKS_PER_PROJECT = 5  # Minimum number of tasks per project
MAX_TASKS_PER_PROJECT = 20  # Maximum number of tasks per project
TASK_SWITCH_INTERVAL = 6   # Max interval (in hours) for random task switching

# Task class


class Task:
    def __init__(self, task_id, project_id, duration):
        self.task_id = task_id
        self.project_id = project_id
        self.duration = duration

# Simulation function


def simulate_team_until_complete_with_limit(num_team_members, num_projects, max_duration):
    # Generate tasks for projects
    tasks = []
    task_id = 1
    for project_id in range(num_projects):
        num_tasks = random.randint(
            MIN_TASKS_PER_PROJECT, MAX_TASKS_PER_PROJECT)
        for _ in range(num_tasks):
            task_duration = random.randint(1, max_duration)
            tasks.append(
                Task(task_id=task_id, project_id=project_id, duration=task_duration))
            task_id += 1

    # Team member activity
    team_activity = {member: [] for member in range(num_team_members)}
    task_queue = tasks[:]
    ongoing_tasks = {}
    project_assignments = {project_id: 0 for project_id in range(num_projects)}
    completed_projects = set()
    time_steps = 0

    while task_queue or any(ongoing_tasks.get(member, {}).get("remaining", 0) > 0 for member in range(num_team_members)):
        time_steps += 1
        for member in range(num_team_members):
            if member in ongoing_tasks and ongoing_tasks[member]["remaining"] > 0:
                # Continue working on current task
                ongoing_tasks[member]["remaining"] -= 1
                task_id = ongoing_tasks[member]["task"].task_id
                team_activity[member].append((time_steps, task_id))
            else:
                # Check if the current task is finished
                if member in ongoing_tasks and ongoing_tasks[member]["remaining"] == 0:
                    completed_task = ongoing_tasks[member]["task"]
                    print(f"Time {time_steps}: Task {completed_task.task_id} from Project {
                          completed_task.project_id} completed.")
                    project_id = completed_task.project_id
                    project_assignments[project_id] -= 1

                    # Check if all tasks for the project are completed
                    if all(
                        task.project_id != project_id
                        or task.duration == 0
                        for task in tasks
                    ):
                        if project_id not in completed_projects:
                            completed_projects.add(project_id)
                            print(f"Time {time_steps}: Project {
                                  project_id} completed.")

                    del ongoing_tasks[member]

                # Switch to a new task randomly every 1-TASK_SWITCH_INTERVAL hours
                if random.randint(1, TASK_SWITCH_INTERVAL) == 1 or member not in ongoing_tasks:
                    if task_queue:
                        # Find a task that respects the 2-member-per-project limit
                        available_tasks = [
                            task for task in task_queue if project_assignments[task.project_id] < 2
                        ]
                        if available_tasks:
                            new_task = random.choice(available_tasks)
                            task_queue.remove(new_task)
                            ongoing_tasks[member] = {
                                "task": new_task, "remaining": new_task.duration}
                            project_assignments[new_task.project_id] += 1
                            team_activity[member].append(
                                (time_steps, new_task.task_id))
                elif member not in ongoing_tasks or ongoing_tasks[member]["remaining"] <= 0:
                    # If the current task is finished, decrement the project assignment count
                    if member in ongoing_tasks and ongoing_tasks[member]["task"].project_id is not None:
                        project_id = ongoing_tasks[member]["task"].project_id
                        project_assignments[project_id] -= 1
                    # Idle if no tasks available
                    team_activity[member].append((time_steps, None))

    return team_activity, tasks, time_steps

# Visualization


def visualize_team_activity_with_completion(team_activity, tasks, time_steps):
    task_colors = {task.task_id: f"C{task.task_id % 10}" for task in tasks}
    fig, ax = plt.subplots(figsize=(15, 8))

    for member, activity in team_activity.items():
        for start_time, task_id in activity:
            if task_id is not None:
                ax.barh(
                    member,
                    width=1,
                    left=start_time,
                    color=task_colors[task_id],
                    edgecolor="black",
                )

    ax.set_yticks(range(len(team_activity)))
    ax.set_yticklabels([f"Team Member {m}" for m in team_activity])
    ax.set_xticks(range(0, time_steps + 1, 10))
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Team Members")
    ax.set_title(f"Team Members' Task Activity Over {
                 time_steps} Hours (Until Completion)")
    ax.grid(True, axis="x", linestyle="--", alpha=0.7)
    plt.show()


# Run simulation with the new limit
team_activity, tasks, total_time_steps = simulate_team_until_complete_with_limit(
    num_team_members=NUM_TEAM_MEMBERS,
    num_projects=NUM_PROJECTS,
    max_duration=MAX_TASK_DURATION,
)

# Visualize
visualize_team_activity_with_completion(team_activity, tasks, total_time_steps)
