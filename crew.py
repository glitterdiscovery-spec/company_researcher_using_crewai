"""
CrewAI Multi-Agent Research Crew
Defines agents, tasks, and the crew for researching any company/product.
"""

import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool
from tools import scrape_website, extract_news_article


def create_research_crew(company_name: str) -> Crew:
    """
    Builds and returns a CrewAI Crew configured to research a given company/product.
    
    Args:
        company_name: The name of the company or product to research.
    
    Returns:
        A configured Crew instance ready to be kicked off.
    """

    # ── Tools ──────────────────────────────────────────────────────────────────
    search_tool = SerperDevTool()

    # ── LLM — supports OpenAI and Gemini via LiteLLM ──────────────────────────
    # Model is set by app.py via RESEARCH_MODEL_NAME env var.
    # OpenAI models: gpt-4o-mini, gpt-4o, gpt-4-turbo (needs OPENAI_API_KEY)
    # Gemini models: gemini/gemini-2.0-flash, gemini/gemini-1.5-flash, etc. (needs GEMINI_API_KEY)
    model_name = os.getenv("RESEARCH_MODEL_NAME", "gpt-4o-mini")
    llm = LLM(model=model_name, temperature=0.3)

    # ── Agent 1 : Web Researcher ───────────────────────────────────────────────
    web_researcher = Agent(
        role="Senior Web Research Specialist",
        goal=(
            f"Gather comprehensive, up-to-date intelligence about '{company_name}' "
            "from across the internet, including news, financials, products, and market position."
        ),
        backstory=(
            "You are an elite web researcher with 10+ years of experience in competitive "
            "intelligence. You are brilliant at crafting targeted search queries to uncover "
            "recent news, product launches, financial disclosures, and strategic moves. "
            "You always cite your sources and are meticulous about finding the most relevant "
            "URLs for deeper investigation."
        ),
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=8,
    )

    # ── Agent 2 : Data Extractor ───────────────────────────────────────────────
    data_extractor = Agent(
        role="Web Data Extraction & Analysis Expert",
        goal=(
            f"Scrape the official website and key online sources for '{company_name}' "
            "to extract rich, detailed information about its products, services, team, "
            "pricing, and technology."
        ),
        backstory=(
            "You are a specialist in extracting signal from noise on the web. Armed with "
            "powerful scraping tools, you visit company websites, press-release pages, and "
            "tech-review sites to pull out structured, actionable data. You cross-reference "
            "multiple sources to ensure accuracy and always highlight the most commercially "
            "relevant findings."
        ),
        tools=[scrape_website, extract_news_article],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=8,
    )

    # ── Agent 3 : Report Editor ────────────────────────────────────────────────
    report_editor = Agent(
        role="Business Intelligence Report Editor",
        goal=(
            f"Synthesise all gathered intelligence about '{company_name}' into a clear, "
            "professional, executive-ready Markdown report with actionable insights."
        ),
        backstory=(
            "You are a senior business intelligence analyst and former McKinsey consultant. "
            "Your superpower is turning raw data and scattered research notes into elegant, "
            "structured reports that tell a compelling story. You write with clarity and "
            "precision, always leading with the most impactful insights."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # ── Task 1 : Web Research ──────────────────────────────────────────────────
    research_task = Task(
        description=(
            f"Conduct a thorough web search investigation of **{company_name}**.\n\n"
            "You MUST search for and collect:\n"
            "1. Company overview: founding year, HQ location, mission, CEO/founders\n"
            "2. Main products or services (with brief descriptions)\n"
            "3. Latest news & announcements (past 6 months) — include dates\n"
            "4. Market position: estimated valuation, revenue, funding rounds\n"
            "5. Key competitors and how {company_name} differentiates itself\n"
            "6. Official website URL and 2-3 other important URLs (news, LinkedIn, Crunchbase)\n"
            "7. Any controversies, challenges, or notable partnerships\n\n"
            "Provide detailed findings WITH sources (URLs). "
            "List the official website URL clearly so it can be scraped next."
        ),
        agent=web_researcher,
        expected_output=(
            "A detailed research brief (500–800 words) containing:\n"
            "- Company background and leadership\n"
            "- Products/services summary\n"
            "- Recent news with dates and source URLs\n"
            "- Market & financial overview\n"
            "- Competitive landscape notes\n"
            "- List of key URLs for scraping (official site, news articles, etc.)"
        ),
    )

    # ── Task 2 : Deep Scraping ─────────────────────────────────────────────────
    extraction_task = Task(
        description=(
            f"Using the URLs discovered by the researcher, scrape and extract detailed "
            f"content about **{company_name}**.\n\n"
            "You MUST:\n"
            "1. Scrape the official company website (homepage + /about, /products, /pricing pages if they exist)\n"
            "2. Extract any news articles or press releases provided\n"
            "3. Identify: pricing tiers, feature lists, technology stack, integrations\n"
            "4. Find customer testimonials, case studies, or notable clients\n"
            "5. Note any recent product updates, roadmap info, or release notes\n"
            "6. Identify partnerships, investors, or strategic alliances mentioned on the site\n\n"
            "Cross-reference your findings with the research brief to fill gaps. "
            "If a URL fails, try an alternative one."
        ),
        agent=data_extractor,
        expected_output=(
            "Structured extracted data (400–600 words) including:\n"
            "- Detailed product/service feature breakdown\n"
            "- Pricing information (if found)\n"
            "- Technology and integrations\n"
            "- Notable customers or case studies\n"
            "- Partnership / investor info\n"
            "- Any interesting facts from the website not found via search"
        ),
        context=[research_task],
    )

    # ── Task 3 : Report Compilation ────────────────────────────────────────────
    report_task = Task(
        description=(
            f"Compile ALL research and extracted data into a polished, comprehensive "
            f"intelligence report about **{company_name}**.\n\n"
            "The report MUST:\n"
            "- Be formatted in clean Markdown with ## and ### headers\n"
            "- Open with a punchy Executive Summary (3-5 sentences)\n"
            "- Cover every section listed in the expected output\n"
            "- Use bullet points for lists, bold for key terms\n"
            "- Include a 'Key Takeaways' section at the end with 3-5 strategic insights\n"
            "- Be readable, professional, and free of filler text\n\n"
            "Do NOT invent information — only use what the researcher and extractor found."
        ),
        agent=report_editor,
        expected_output=(
            "A complete Markdown report with the following sections:\n\n"
            "## 🔍 Executive Summary\n"
            "## 🏢 Company Overview\n"
            "## 🚀 Products & Services\n"
            "## 📰 Recent News & Developments\n"
            "## 🏆 Market Position & Competitive Landscape\n"
            "## 💰 Financial Highlights\n"
            "## 🤝 Key Partnerships & Integrations\n"
            "## 💡 Key Takeaways & Strategic Insights\n"
        ),
        context=[research_task, extraction_task],
    )

    # ── Crew ───────────────────────────────────────────────────────────────────
    crew = Crew(
        agents=[web_researcher, data_extractor, report_editor],
        tasks=[research_task, extraction_task, report_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew
