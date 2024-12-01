import random
import matplotlib.pyplot as plt
import pandas as pd

# Constants
NUM_TEAM_MEMBERS = 15
MAX_TASK_DURATION = 72
MIN_TASKS_PER_PROJECT = 5
MAX_TASKS_PER_PROJECT = 20
TASK_SWITCH_INTERVAL = 6
MAX_NEW_TASK_DURATION = 2
OVERHEAD_MULTIPLIER = 0.1  # Overhead added per active project per time step

# Skills
TEAM_SKILLS = {0: "frontend", 1: "backend", 2: "design", 3: "marketing"}
SKILLS = ["frontend", "backend", "design", "marketing"]

# Task class with dependencies and required skills


class Task:
    def __init__(self, task_id, project_id, duration, dependencies, skill):
        self.task_id = task_id
        self.project_id = project_id
        self.duration = duration
        self.dependencies = dependencies
        self.skill = skill
        self.completed = False

# Generate tasks with dependencies, skills, and staggered project start times


def generate_tasks(num_projects, max_duration):
    tasks = []
    project_start_times = {}
    task_id = 1
    for project_id in range(num_projects):
        # Add a start delay for the project
        project_start_times[project_id] = random.randint(0, 50)
        num_tasks = random.randint(
            MIN_TASKS_PER_PROJECT, MAX_TASKS_PER_PROJECT)
        project_tasks = []
        for _ in range(num_tasks):
            task_skill = random.choice(SKILLS)
            task_duration = random.randint(1, max_duration)
            dependencies = random.sample(
                [t.task_id for t in project_tasks], k=random.randint(0, len(project_tasks))
            )
            task = Task(
                task_id=task_id,
                project_id=project_id,
                duration=task_duration,
                dependencies=dependencies,
                skill=task_skill,
            )
            project_tasks.append(task)
            tasks.append(task)
            task_id += 1
    return tasks, project_start_times

# Check if all dependencies are completed


def are_dependencies_completed(task, task_map):
    return all(task_map[dep].completed for dep in task.dependencies)

# Simulation function with staggered project starts


def simulate_with_dependencies_and_overhead(num_team_members, num_projects, max_duration):
    tasks, project_start_times = generate_tasks(num_projects, max_duration)
    task_map = {task.task_id: task for task in tasks}
    team_activity = {member: [] for member in range(num_team_members)}
    ongoing_tasks = {}
    active_projects = set()
    task_queue = tasks[:]
    time_steps = 0
    context_switches = {member: 0 for member in range(
        num_team_members)}  # Track context switches

    while task_queue or any(ongoing_tasks.get(member, {}).get("remaining", 0) > 0 for member in range(num_team_members)):
        time_steps += 1
        active_projects = {
            ongoing_tasks[member]["task"].project_id for member in ongoing_tasks if ongoing_tasks[member]["remaining"] > 0}
        overhead = len(active_projects) * OVERHEAD_MULTIPLIER

        for member in range(num_team_members):
            if member in ongoing_tasks and ongoing_tasks[member]["remaining"] > 0:
                ongoing_tasks[member]["remaining"] -= 1 + overhead
                task_id = ongoing_tasks[member]["task"].task_id
                team_activity[member].append((time_steps, task_id))
            else:
                if member in ongoing_tasks and ongoing_tasks[member]["remaining"] <= 0:
                    completed_task = ongoing_tasks[member]["task"]
                    completed_task.completed = True
                    del ongoing_tasks[member]

                # Assign new tasks that match the team member's skill, dependencies, and project start time
                available_tasks = [
                    task for task in task_queue
                    if TEAM_SKILLS[member % len(TEAM_SKILLS)] == task.skill
                    and are_dependencies_completed(task, task_map)
                    # Check project start time
                    and time_steps >= project_start_times[task.project_id]
                ]
                if available_tasks:
                    new_task = random.choice(available_tasks)
                    task_queue.remove(new_task)

                    # Increment context switch if switching tasks
                    if member in ongoing_tasks:
                        context_switches[member] += 1

                    ongoing_tasks[member] = {
                        "task": new_task,
                        "remaining": new_task.duration,
                    }
                    team_activity[member].append(
                        (time_steps, new_task.task_id))
                else:
                    team_activity[member].append((time_steps, None))

    return team_activity, tasks, time_steps, context_switches, project_start_times

# Generate an overview report


def generate_overview_report(tasks, time_steps, num_projects):
    total_tasks = len(tasks)
    average_duration = sum(task.duration for task in tasks) / total_tasks
    print("\n--- Simulation Overview Report ---")
    print(f"Number of Projects: {num_projects}")
    print(f"Total Number of Tasks: {total_tasks}")
    print(f"Average Task Duration: {average_duration:.2f} hours")
    print(f"Total Time Steps: {time_steps}")
    print("\n--- Task Details ---")
    for project_id in sorted(set(task.project_id for task in tasks)):
        project_tasks = [
            task for task in tasks if task.project_id == project_id]
        print(f"Project {project_id}: {len(project_tasks)} tasks")

# Visualization functions for results


def visualize_results_table_and_chart(results):
    df = pd.DataFrame(list(results.items()), columns=[
                      "Number of Projects", "Average Completion Time"])
    print("\nResults Table:")
    print(df.to_string(index=False))
    plt.figure(figsize=(10, 6))
    plt.plot(df["Number of Projects"],
             df["Average Completion Time"], marker="o", linestyle="-")
    plt.title("Impact of Number of Projects on Average Completion Time")
    plt.xlabel("Number of Projects")
    plt.ylabel("Average Completion Time (hours)")
    plt.grid(True)
    plt.savefig("results.png", dpi=300)

# Run simulation and analyze


def run_simulation_with_improvements(num_team_members, project_range, max_task_duration, iterations=2):
    results = {}
    for num_projects in project_range:
        total_time_steps = 0
        tasks_report = None

        for iteration in range(iterations):
            print(f"\nIteration {iteration + 1} for {num_projects} projects:")
            team_activity, tasks, time_steps, context_switches, project_start_times = simulate_with_dependencies_and_overhead(
                num_team_members=num_team_members,
                num_projects=num_projects,
                max_duration=max_task_duration,
            )
            total_time_steps += time_steps
            if iteration == 1:  # Generate overview for the first iteration
                generate_overview_report(tasks, time_steps, num_projects)

        average_time = total_time_steps / iterations
        results[num_projects] = average_time
        print(f"Projects: {num_projects}, Average Completion Time: {
              average_time:.2f} hours")

    return results


# Define the range of projects and run the simulation
project_range = range(1, 31)  # Run for one specific project count
iterations = 20  # Run a single iteration
average_completion_times = run_simulation_with_improvements(
    num_team_members=NUM_TEAM_MEMBERS,
    project_range=project_range,
    max_task_duration=MAX_TASK_DURATION,
    iterations=iterations,
)

# Visualize results
visualize_results_table_and_chart(average_completion_times)
