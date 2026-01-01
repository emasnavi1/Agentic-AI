from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from email_writer_agent import email_writer_agent, EmailContent
import asyncio

class ResearchManager:

    async def run(self, query: str):
        """ Run the deep research process, yielding the status updates and the final report"""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting research...")
            search_plan = await self.plan_searches(query)
            yield "Searches planned, starting to search..."     
            search_results = await self.dispatch_searches(search_plan)
            yield "Searches complete, writing report..."
            report = await self.write_report(query, search_results)
            yield "Report written, preparing email..."
            email_content = await self.prepare_email(report.model_dump_json())
            yield "Sending Email..."
            await self.send_email(email_content.model_dump_json())
            yield "Email sent, research complete"
            yield email_content.message_body
        

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """ Plan the searches to perform for the query """
        print("Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def dispatch_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """ Dispatch the searches to perform search for the query """
        print("Searching...")
        # num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        # for task in asyncio.as_completed(tasks):
        #     result = await task
        #     if result is not None:
        #         results.append(result)
        #     num_completed += 1
        #     print(f"Searching... {num_completed}/{len(tasks)} completed")
        # print("Finished searching")
        raw_results = await asyncio.gather(*tasks)
        results = [r for r in raw_results if r is not None]
        print(f"Finished doing research. Did {len(results)} searches out of {len(search_plan.searches)} subjects.")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """ Perform a search for the query """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """ Write the report for the query """
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input,
        )

        print("Finished writing report")
        return result.final_output_as(ReportData)
    
    async def prepare_email(self, report: ReportData) -> EmailContent:
        """Prepare an email to be fed to te send email agent"""
        print("Deciding about email subject and body, writing the email ...")
        result = await Runner.run(email_writer_agent, report)
        return result.final_output_as(EmailContent)
        
    
    async def send_email(self, emailContent: EmailContent) -> None:
        print("Sending the email...")
        result = await Runner.run(
            email_agent,
            emailContent,
        )
        print("Email sent")
        return