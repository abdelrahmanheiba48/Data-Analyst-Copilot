from crewai import Crew, Process
import agents, tasks

context_crew = Crew(
    agents=[agents.Business_Context_Architect],
    tasks=[tasks.understanding_task],
    process=Process.sequential,
)

retrieval_count_crew = Crew(
    agents=[agents.Query_Understanding_Agent, agents.Retrieval_Count_Agent],
    tasks=[tasks.query_understanding_task, tasks.Required_column_task],
    process=Process.sequential,
)

code_crew = Crew(
    agents=[agents.Data_Analysis_Code_Agent],
    tasks=[tasks.data_analysis_code_task],
    process=Process.sequential,
)

print(retrieval_count_crew.kickoff())