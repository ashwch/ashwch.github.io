Title: Evolving Engineering Recruitment at Diversio in the Age of AI
Date: 2025-02-23
Modified: 2025-02-23
Category: Hiring
Tags: hiring, interviewing, ai, diversio, lessons-learned, best-practices
Slug: evolving-engineering-recruitment-at-diversio-in-the-age-of-ai
Authors: Ashwini Chaudhary
Summary: What we have learned hiring at Diversio

## Table of Contents

1. [Introduction & Evolution at Diversio](#introduction-evolution-at-diversio)
2. [How We Used to Do It (Pre-ChatGPT)](#how-we-used-to-do-it-pre-chatgpt)
   - [Resume Screening](#resume-screening)
   - [Take Home Exercises](#take-home-exercises)
   - [Zoom Interview](#zoom-interview)
3. [Interviewing in 2025](#interviewing-in-2025)
   - [Posting the Job Ad](#posting-the-job-ad)
   - [Filtering Resumes](#filtering-resumes)
   - [Screening Round](#screening-round)
   - [Coding Round](#coding-round)
   - [Final Round](#final-round)

---

# Introduction & Evolution at Diversio

At Diversio, our hiring process has evolved significantly over the years. In our early days, we relied heavily on detailed resume screenings and take-home exercises. Today, we’ve adapted to a new landscape where remote hiring, AI-assisted filtering, and a streamlined interview process help us manage the increased applicant volume while ensuring we find the best long-term fits.

**Key Changes at a Glance:**

- Transition from take-home exercises to real-time, remote interviews.
- Adoption of AI tools (like our custom GPT) to efficiently filter resumes.
- Increased focus on cultural fit and long-term alignment.
- Emphasis on transparent, remote hiring practices.

# How We Used to Do It (Pre-ChatGPT)

We were very lucky in terms of hiring at Diversio until 2023—we had an excellent attrition rate and were fortunate to hire very talented interns from the University of Toronto, University of Waterloo, and Queen's University. The full-time hires were mostly referrals.

### 1. Resume Screening

A resume screening was conducted by myself and the PM, including checking candidates' past co-op remarks from other companies.

### 2. Take Home Exercises

We have a strong belief in asking questions that are directly relevant to what a candidate will do on a day-to-day basis at Diversio.

Depending on the position, we provided a different set of questions. Our exercises included:

- **Programming Puzzle:**  
  Based on an internal algorithm and a problem we had solved in the past, this puzzle was reworded to sound engaging. The code was expected to be well documented and pass the test cases mentioned in the Python script.

  Goals here were:

  - Are they able to follow a complex problem statement (including the provided examples)?
  - Can they fill in the gaps? (i.e., how would they approach tasks at Diversio when some information is not mentioned explicitly, requiring them to figure it out on their own or use their best judgment?)
  - Can they identify edge cases on their own?
  - Can they write readable, well-documented code?

- **Command Line Script:**  
  A task to parse our status page and provide details on how our apps have been performing over the past six months, including identifying the minimum and maximum response times of a service.

  Goals here were:

  - Are they able to parse HTML source code?
  - Are they inspecting elements to see if there are any internal APIs they can utilize?
  - Do they know how to build command-line utilities? (This is a skill we use frequently at Diversio.)
  - How is their code structure, documentation, and testing?

Candidates were expected to submit their solutions on GitHub, which we then reviewed (by myself and other engineers) and provided feedback on.

### 3. Zoom Interview

#### Walkthrough and Discussing Their Solutions

Candidates whose solutions passed our internal review were invited to a Zoom interview. During this round, we discussed their take-home exercises in depth—asking them to explain their solutions and thought processes, and throwing in some edge cases or tweaking the requirements to see if they could adapt their solution on the fly.

#### Real-Time Code Review

At Diversio, we invest a significant amount of time in code reviews because we believe that the effort not only benefits the company but also provides an opportunity to teach and learn from each other.

For this, we used a Python script deliberately filled with poorly written code—ignoring best practices, using inefficient data structures, and exhibiting problematic file I/O, networking, and error handling. The candidate was asked to explain what each section of the script did and to propose better solutions for each section or function, along with justifications.

Goals here were:

- To determine if they focus on solving the underlying problem rather than just critiquing the code.
- To assess their ability to read and understand someone else’s code.
- To gauge their knowledge of best practices and their ability to identify poor coding practices.

We allowed candidates to use Google during the interviews to look up anything they didn’t know. Since their screen was shared with us, we could observe how they searched for information and selected among the different results.

# Interviewing in 2025

A lot has changed since 2023:

- We are a much bigger company now, so when we post a job, we receive many more applicants.
- Many layoffs in big tech companies and AI's impact on dev jobs are resulting in significantly more applicants.
- Take-home interviews have been phased out in favor of real-time evaluations.
- Candidates are using resume tools to trick ATS auto-screening into thinking their resumes are the best.
- Remote hiring is the norm.

### Posting the Job Ad

We use Collage internally, which automatically posts the job on Indeed. In addition, we use Instahyre and [Hasjob](https://hasjob.co/). I also post about it on my LinkedIn to increase its reach.

#### When to Post?

We have found that posting on Friday works best for us. Within the first two days, we received around 400 applicants, and since it was the weekend, I had enough time to review them and filter out those who appeared promising. This built a pipeline for the next 1–2 weeks that was within our team’s capacity.

### Filtering Resumes

- **Size of Resume:**
  Resumes longer than 1–2 pages are a direct reject, including those where candidates list every 10–20 bullet points under every role.

- **Tenures:**  
  Short tenures at multiple places are a red flag, as they increase the likelihood of job-hopping. At Diversio, we want to invest in people for the long term.

- **Work History:**
  We prefer candidates with experience at product startups over service-based companies. We also assess how they explain the features they have worked on—whether they are concise and to the point or merely rely on buzzwords.  
  Resumes that boast metrics like "x% improvement in signups/deployment" or "y% reduction in bugs" without proper context are directly rejected. Such figures often result from attempts to game ATS auto-screening and, frankly, are often meaningless—even after 12 years as a software engineer I don't have such stats myself.

- **GitHub and Portfolio (if any):**  
  We look at candidates’ pinned repositories. Boilerplate projects, past interview tasks, or college projects aren’t meaningful to us—we value significant contributions, a robust commit history, and open-source work.

- **LinkedIn:**  
  We verify that the candidate’s LinkedIn profile matches their resume, that the listed companies are credible, and we review their post history.

#### ChatGPT

To speed up the filtering process, we use a custom GPT tool that evaluates most of the above criteria (except for the last two points), assigning points to each resume so that we can sort them efficiently.

### Screening Round

Candidates selected after resume screening go through a screening round with a senior engineer at Diversio. We require screen sharing and that the camera be turned on to ensure there is no cheating. Candidates are allowed to use Google—but only on the shared screen.

The goal of this 30–45 minute call is to:

- Check their communication skills.
- Explain Diversio, the job, and its requirements.
- Walk through their resume, asking counter-questions to verify their project experience.
- Check basic coding skills that shouldn’t require any preparation.
- Discuss their notice period and salary expectations.

Candidates are then ranked based on feedback, and top performers move forward.

### Coding Round

This round is conducted with the senior engineer leading the respective department (backend or frontend). It is a 1h 15min to 1h 30min call during which the candidate is required to share their screen and have their camera turned on.

This call includes:
- In-depth technical discussions around backend or frontend topics.
- Solving two coding questions and explaining their approach.

### Final Round

The final round is a non-technical interview with me, reserved for candidates who performed exceptionally in the screening and coding rounds and met our criteria.

This interview is designed to provide a holistic view of the candidate by:

- **Creating a Comfortable Environment:** Beginning with a relaxed introduction that encourages open conversation.
- **Assessing Collaboration & Adaptability:** Exploring how candidates navigate teamwork challenges and manage unexpected changes within dynamic environments.
- **Evaluating Cultural & Career Fit:** Discussing work styles, long-term aspirations, and feedback experiences to ensure alignment with Diversio’s team values.
- **Setting Clear Role Expectations:** Clarifying work dynamics such as flexible hours and communication preferences, while highlighting Diversio’s vision and engineering culture.
