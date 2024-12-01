import random
import matplotlib.pyplot as plt

# Constants
NUM_TEAM_MEMBERS = 15  # Number of team members
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

# Run simulation and analyze


def run_simulation_and_analyze(num_team_members, project_range, max_task_duration, iterations=100):
    results = {}

    for num_projects in project_range:
        total_time_steps = 0

        for _ in range(iterations):
            _, _, time_steps = simulate_team_until_complete_with_limit(
                num_team_members=num_team_members,
                num_projects=num_projects,
                max_duration=max_task_duration,
            )
            total_time_steps += time_steps

        average_time = total_time_steps / iterations
        results[num_projects] = average_time
        print(f"Projects: {num_projects}, Average Completion Time: {
              average_time:.2f} hours")

    return results

# Visualization


def visualize_average_completion_times(results):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(results.keys(), results.values(), edgecolor="black")
    ax.set_xlabel("Number of Projects")
    ax.set_ylabel("Average Completion Time (hours)")
    ax.set_title("Average Project Completion Time by Number of Projects")
    plt.xticks(list(results.keys()))
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()


# Define the range of projects (3 to 20) and run the simulation
project_range = range(1, 30)  # From 3 to 20 projects
iterations = 10  # Number of iterations for each simulation

# Run the simulation and analyze
average_completion_times = run_simulation_and_analyze(
    num_team_members=NUM_TEAM_MEMBERS,
    project_range=project_range,
    max_task_duration=MAX_TASK_DURATION,
    iterations=iterations,
)

# Visualize the results
visualize_average_completion_times(average_completion_times)
