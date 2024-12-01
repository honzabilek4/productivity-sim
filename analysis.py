# analysis.py

import random
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from mesa import Agent, Model
from mesa.agent import AgentSet
from mesa.datacollection import DataCollector

# Team Member Agent


class TeamMember(Agent):
    def __init__(self, unique_id, model):
        Agent.__init__(self, model)
        self.projects = []  # List of projects this team member is working on
        self.productivity = 1.0  # Base productivity
        self.interactions = set()  # Store IDs of interacted team members
        self.context_switching_time = 0  # Initialize context switching time

    def step(self):
        # Calculate productivity
        num_projects = len(self.projects)
        if num_projects > 1:
            # Simulate context-switching penalty
            self.productivity = 1 / np.sqrt(num_projects)
        else:
            self.productivity = 1.0

        # Calculate context switching time
        self.context_switching_time = self.calculate_context_switching_time(
            num_projects)

        # Simulate interactions
        self.interact_with_team_members()

    def calculate_context_switching_time(self, num_projects):
        # Assume context switching time increases exponentially
        base_time = 1  # Base time unit
        return base_time * (num_projects - 1) ** 1.5 if num_projects > 1 else 0

    def interact_with_team_members(self):
        # Find team members working on the same projects
        for project in self.projects:
            # Get all agents working on the same project
            team_members = [
                agent for agent in self.model.agent_set
                if agent != self and project in agent.projects
            ]
            # Record interactions
            for member in team_members:
                self.interactions.add(member.unique_id)

# Project Model


class ProjectModel(Model):
    def __init__(self, num_agents, num_projects):
        Model.__init__(self)
        self.num_agents = num_agents
        self.num_projects = num_projects
        self.random = random.Random()
        self.running = True

        # Create AgentSet to manage agents
        self.agent_set = AgentSet([], self.random)

        # Create agents and add them to the AgentSet
        for i in range(self.num_agents):
            agent = TeamMember(i, self)
            self.agent_set.add(agent)

        # Assign projects to agents
        self.projects = list(range(self.num_projects))

        # Decide how many projects each agent should have
        percentage = 0.5  # Adjust this percentage as needed
        projects_per_agent = max(1, int(self.num_projects * percentage))

        for agent in self.agent_set:
            # Randomly assign projects to each agent
            assigned_projects = self.random.sample(
                self.projects, k=min(projects_per_agent, self.num_projects)
            )
            agent.projects.extend(assigned_projects)

        # Collect data
        self.datacollector = DataCollector(
            model_reporters={
                "Avg Productivity": self.compute_avg_productivity,
                "Avg Context Switching Time": self.compute_avg_context_switching_time,
                "Total Interactions": self.compute_total_interactions,
            },
            agent_reporters={
                "Productivity": "productivity",
                "Context Switching Time": "context_switching_time",
            },
        )

    def step(self):
        self.datacollector.collect(self)
        # Randomly shuffle agents to simulate random activation
        agent_list = list(self.agent_set)
        self.random.shuffle(agent_list)
        for agent in agent_list:
            agent.step()

    def run_model(self, steps):
        for _ in range(steps):
            self.step()

    def compute_avg_productivity(self):
        return np.mean([agent.productivity for agent in self.agent_set])

    def compute_avg_context_switching_time(self):
        return np.mean([agent.context_switching_time for agent in self.agent_set])

    def compute_total_interactions(self):
        interaction_pairs = self.collect_interaction_data()
        return len(interaction_pairs)

    def collect_interaction_data(self):
        # Collect interactions from all agents
        interaction_pairs = set()
        for agent in self.agent_set:
            for other_id in agent.interactions:
                # Create a sorted tuple to avoid duplicate edges
                edge = tuple(sorted((agent.unique_id, other_id)))
                interaction_pairs.add(edge)
        return interaction_pairs

# Visualization Functions


def visualize_interactions(model, num_projects):
    interaction_pairs = model.collect_interaction_data()

    # Create a graph
    G = nx.Graph()
    G.add_nodes_from(range(model.num_agents))
    G.add_edges_from(interaction_pairs)

    # Draw the graph
    plt.figure(figsize=(8, 8))
    pos = nx.spring_layout(G, seed=42)  # Seed for reproducibility
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=500)
    nx.draw_networkx_edges(G, pos, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=10, font_color='black')

    plt.title(f"Team Member Interactions with {num_projects} Projects")
    plt.axis('off')
    plt.show()


def plot_results(productivity_results, context_switching_results, interaction_results):
    # Plot Productivity vs. Number of Projects
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.plot(list(productivity_results.keys()), list(
        productivity_results.values()), marker="o")
    plt.title("Productivity vs. Number of Projects")
    plt.xlabel("Number of Projects")
    plt.ylabel("Average Productivity")
    plt.grid(True)

    # Plot Context Switching Time vs. Number of Projects
    plt.subplot(1, 3, 2)
    plt.plot(list(context_switching_results.keys()), list(
        context_switching_results.values()), marker="o", color='orange')
    plt.title("Context Switching Time vs. Number of Projects")
    plt.xlabel("Number of Projects")
    plt.ylabel("Average Context Switching Time")
    plt.grid(True)

    # Plot Total Interactions vs. Number of Projects
    plt.subplot(1, 3, 3)
    plt.plot(list(interaction_results.keys()), list(
        interaction_results.values()), marker="o", color='green')
    plt.title("Total Interactions vs. Number of Projects")
    plt.xlabel("Number of Projects")
    plt.ylabel("Total Interactions")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# Run the Simulation


def run_simulation(num_agents=15, max_projects=5, steps=10):
    productivity_results = {}
    context_switching_results = {}
    interaction_results = {}
    for num_projects in range(1, max_projects + 1):
        model = ProjectModel(num_agents=num_agents, num_projects=num_projects)
        model.run_model(steps)
        model_data = model.datacollector.get_model_vars_dataframe()
        avg_productivity = model_data["Avg Productivity"].mean()
        avg_context_switching = model_data["Avg Context Switching Time"].mean()
        total_interactions = model_data["Total Interactions"].iloc[-1]
        productivity_results[num_projects] = avg_productivity
        context_switching_results[num_projects] = avg_context_switching
        interaction_results[num_projects] = total_interactions

        # Visualize interactions for this number of projects
        visualize_interactions(model, num_projects)

    return productivity_results, context_switching_results, interaction_results


if __name__ == "__main__":
    # Ensure required packages are installed
    try:
        import networkx as nx
    except ImportError:
        print("NetworkX is required for visualization. Install it using 'pip install networkx'")
        exit(1)

    # Run the simulation and collect results
    productivity_results, context_switching_results, interaction_results = run_simulation(
        num_agents=15, max_projects=5, steps=10
    )

    # Plot the results
    plot_results(productivity_results,
                 context_switching_results, interaction_results)
