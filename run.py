from mesa import Agent, Model
from mesa.time import RandomActivation
import random


class Task:
    def __init__(self, project_id, duration, is_review=False):
        self.project_id = project_id
        self.duration = duration  # Time required to complete the task
        self.is_review = is_review  # Whether the task is a review task


class TeamMember(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.current_task = None
        self.time_remaining = 0

    def assign_task(self, task):
        self.current_task = task
        self.time_remaining = task.duration

    def step(self):
        if self.current_task:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                # Task completed
                if self.current_task.is_review:
                    # Review task completed
                    self.model.mark_task_complete(self.current_task)
                else:
                    # Main task completed, generate review task
                    self.model.generate_review_task(self.current_task)
                self.current_task = None
        else:
            # If no task, pick a random task from the queue
            if self.model.task_queue:
                random_task = random.choice(self.model.task_queue)
                self.model.task_queue.remove(random_task)
                self.assign_task(random_task)


class StartupModel(Model):
    def __init__(self, num_team_members, num_projects, seed=None):
        super().__init__(seed=seed)
        self.schedule = RandomActivation(self)
        self.task_queue = []
        self.projects = {i: {"tasks_remaining": 0, "start_time": None,
                             "end_time": None} for i in range(num_projects)}
        self.time = 0

        # Generate initial tasks
        for project_id in range(num_projects):
            num_tasks = random.randint(5, 20)
            self.projects[project_id]["tasks_remaining"] = num_tasks
            for _ in range(num_tasks):
                task_duration = random.randint(1, 10)
                self.task_queue.append(Task(project_id, task_duration))

        # Add team members
        for i in range(num_team_members):
            member = TeamMember(i, self)
            self.schedule.add(member)

    def generate_review_task(self, completed_task):
        # Generate a review task with shorter duration
        review_task_duration = random.randint(1, 3)  # Review tasks are shorter
        review_task = Task(
            project_id=completed_task.project_id,
            duration=review_task_duration,
            is_review=True
        )
        self.task_queue.append(review_task)

    def mark_task_complete(self, task):
        if task.project_id is not None:
            project = self.projects[task.project_id]
            project["tasks_remaining"] -= 1
            if project["start_time"] is None:
                project["start_time"] = self.time
            if project["tasks_remaining"] == 0:
                project["end_time"] = self.time

    def step(self):
        self.time += 1
        self.schedule.step()


def run_simulation(num_projects, num_team_members, num_runs):
    completion_times = []

    for _ in range(num_runs):
        model = StartupModel(
            num_team_members=num_team_members, num_projects=num_projects)
        while any(project["end_time"] is None for project in model.projects.values()):
            model.step()
        project_times = [
            project["end_time"] - project["start_time"]
            for project in model.projects.values()
            if project["end_time"] is not None
        ]
        completion_times.extend(project_times)

    average_time = sum(completion_times) / len(completion_times)
    return average_time


if __name__ == "__main__":
    results = {}
    num_runs = 5
    team_size = 5

    for projects in range(1, 6):  # Vary number of simultaneous projects from 1 to 5
        avg_time = run_simulation(
            num_projects=projects, num_team_members=team_size, num_runs=num_runs)
        results[projects] = avg_time
        print(f"Average completion time for {
              projects} projects: {avg_time:.2f} time units")

    print("\n--- Summary ---")
    for projects, avg_time in results.items():
        print(f"{projects} projects: {avg_time:.2f} time units")
