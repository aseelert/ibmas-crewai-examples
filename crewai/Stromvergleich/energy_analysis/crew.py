from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, DirectoryReadTool, FileReadTool

search_tool = SerperDevTool(
    search_url="https://google.serper.dev/search",
    country="de",
    locale="de",
    n_results=100
)


@CrewBase
class EnergyAnalysisCrew:
    """Energy Analysis crew for analyzing German energy tariffs"""

    @agent
    def company_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['company_research_agent'],
            tools=[search_tool, ScrapeWebsiteTool()],
            verbose=True
        )

    @agent
    def tariff_specialist_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['tariff_specialist_agent'],
            tools=[search_tool, ScrapeWebsiteTool()],
            verbose=True
        )

    @agent
    def comparison_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['comparison_agent'],
            tools=[search_tool, ScrapeWebsiteTool()],
            verbose=True
        )

    @agent
    def report_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['report_agent'],
            tools=[DirectoryReadTool(directory='./outputs'), FileReadTool()],
            verbose=True
        )

    @task
    def market_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_research_task']
        )

    @task
    def tariff_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['tariff_analysis_task']
        )

    @task
    def comparison_task(self) -> Task:
        return Task(
            config=self.tasks_config['comparison_task']
        )

    @task
    def recommendation_task(self) -> Task:
        return Task(
            config=self.tasks_config['recommendation_task']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Energy Analysis crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=True
        )