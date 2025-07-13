Title: Postman to Bruno: A Weekend Migration That Transformed Our API Workflow
Date: 2025-07-13
Modified: 2025-07-13
Category: Engineering
Tags: postman, bruno, api, ai, claude-code, productivity, diversio, engineering, tooling, developer-experience
Slug: from-postman-to-bruno-how-ai-changed-our-api-workflow
Authors: Ashwini Chaudhary
Summary: We migrated our entire Postman collection to Bruno over a weekend and leveraged Claude Code to automate API documentation, reducing documentation time by 90% and catching breaking changes at review time.

> We moved our entire Postman collection to Bruno over a weekend and let Claude Code chew on the new files by Monday morning. By lunchtime, API docs were writing themselves.

---

## Table of Contents

1. [What you'll learn](#what-youll-learn)
2. [Why we relied on Postman for so long & where it falls short](#why-we-relied-on-postman-for-so-long--where-it-falls-short)
3. [Migration basics](#migration-basics)
4. [Scripts that saved us hours](#scripts-that-saved-us-hours)
5. [Common Migration Patterns](#common-migration-patterns)
6. [The AI Integration Revolution](#the-ai-integration-revolution)
7. [The Unexpected Benefits](#the-unexpected-benefits)
8. [Getting Your Team Started](#getting-your-team-started)
9. [What This Means for Engineering Teams](#what-this-means-for-engineering-teams)

---

## What you'll learn
  
- **Migrate** a Postman collection (requests _and_ environments) to Bruno in a few hours.
- **Keep docs in‑lockstep** with your codebase; no more stale Postman descriptions.
- **Let AI write the boring bits:** type `/bruno-api path/to/request.bru` and get ready‑to‑ship docs, TypeScript types, and React Query hooks.
- **Catch breaking changes at review time,** not after deploy night.

If you're exploring AI‑first tooling and looking to streamline your API workflow, this guide walks you through our practical migration step‑by‑step. If you're already using Bruno, you'll learn how to help improve your existing workflow further using AI.

---

## Why we relied on Postman for so long & where it falls short

At [Diversio](https://diversio.com/), Postman had been our all‑purpose API toolkit since the company's first endpoint shipped in 2018. Every engineer has owned a collection or three; shared environments lived in the cloud; QA and PMs could fire requests without touching the codebase.

**Why Postman Works for Us (So Far)**

- _Scriptable_: Pre‑request scripts spun up test users, refreshed auth tokens, and handled auth with a single click.
    
- _Variable templating_: `{{base_url}}`, `{{auth_token}}`, and other vars kept requests DRY across local and cloud setups.
    
- _Chained workflows_: Scripts set environment variables that downstream requests consumed, so multi‑step API flows ran end‑to‑end without anyone hand‑editing the shared collection.
    
- _Performance‑testing ready_: The same collections powered our performance tests, giving us baseline latency numbers without duplicating effort.
    
- _Full‑stack friendly_: Frontend and backend engineers could debug and iterate on the same requests without context‑switching or extra tooling.
    
- _Collaborative_: Share links meant non‑engineers could poke endpoints in seconds.

### Why it started to hurt

As our API surface has increased and now we are working on more and more features at once(thanks to agentic coding), the workflow that once felt effortless began eating hours and hurting our productivity.

- **Manual sync tax** – Every new endpoint meant combing through multiple collections to wire up scripts, tests, and examples by hand.
    
- **Docs drift** – Descriptions hid in Postman's UI; unless someone remembered to update them, they slipped out of date.
    
- **Invisible breaking changes** – Because collections lived in Postman's cloud, reviewers never saw contract updates during code review.
    
- **Meeting creep** – We still ended up on calls to reconcile mismatched examples and edge‑case behaviours. A lot of time spent in huddles and stand-ups discussing APIs that we couldn't document well inside of Postman.

Postman still _works_ but it has just slowed us down. Any change meant updating code _and_ a JSON export no one liked opening. That lag became the bottleneck.

[Bruno](https://www.usebruno.com/)'s Git‑friendly plain‑text format, and its ability to embed full Markdown docs, looked like a way out. The best part? AI agents can read `.bru` files like normal code, so automation suddenly became trivial and APIs are now part of our codebase and included in diffs during code reviews.

## Migration basics

### 1. Script syntax

```js
// Postman
var json = JSON.parse(responseBody);
var token = json["access_token"];
pm.environment.set("auth_token", token);

// Bruno
var json = res.getBody();
var token = json.access_token;
bru.setEnvVar("auth_token", token);
```

### 2. Base64 helpers

```js
// Postman
const payload = JSON.parse(atob(token.split('.')[1]));

// Bruno (Buffer.from works in Bruno's Node.js environment)
const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
```

### 3. Environment files

```bru
vars {
  base_url: http://localhost:8000
  api_key: {{process.env.API_KEY}}
}
```

### 4. In‑line Markdown docs

Bruno lets every request double as a mini README:

```bru
docs {
  # User Authentication
  
  `POST` `/api/v2/auth/login`

  ## Overview

  Returns JWT tokens.

  ⚡ **Rate Limit**: 5/min per IP

  ...
}
```

Rich tables, code fences, emojis etc can be included. Because it's Markdown, Claude Code and other AI tools parse it effortlessly.

### 5. Organizing your Bruno collections

After migration, we organized our Bruno files by feature rather than by API version. Here's our structure:

```text
bruno/
├── .env                  # Local secrets (git-ignored)
├── .env.example          # Template for team members
├── .gitignore           # Ensures .env stays local
├── environments/
│   ├── local.bru
│   ├── staging.bru
│   └── production.bru
├── auth/
│   ├── login.bru
│   ├── refresh_token.bru
│   └── logout.bru
├── users/
│   ├── get_profile.bru
│   ├── update_profile.bru
│   └── list_users.bru
├── analytics/
│   ├── dashboard_metrics.bru
│   └── export_reports.bru
└── integrations/
    ├── stripe/
    │   └── create_payment.bru
    └── webhooks/
        └── incoming_webhooks.bru
```

**Security tip**: Always add `.env` to your `.gitignore`. Create a `.env.example` with dummy values so team members know what environment variables to set:

```bash
# .env.example
API_BASE_URL=http://localhost:8000
API_KEY=your-api-key-here
JWT_TOKEN=will-be-set-by-login-script
DEFAULT_COMPANY_ID=1234
TEST_USERNAME=testuser
TEST_PASSWORD=testpass
```

Each `.bru` file can include documentation, pre/post scripts, and environment variable references. This structure makes it easy to:

- Find related endpoints quickly
- Review API changes in PRs
- Generate documentation by feature area
- Manage permissions at the folder level
- Keep sensitive data out of version control

---

## Scripts that saved us hours

### Environment converter (Python)

The script is available in this GitHub gist: [migrate_postman_envs.py](https://gist.github.com/ashwch/317ce7d35dd605187bedf39e6b7858a8)

#### Command

```bash
$ uv run migrate_postman_envs.py ./postman_environments/ ./bruno_environments/
```
#### Output

```text
🔄 Processing 10 file(s)...

✅ Converted webhook_env.json → ./bruno_environments/webhook_env.bru
✅ Converted local_env.json → ./bruno_environments/local_env.bru
✅ Converted production.json → ./bruno_environments/production.bru
✅ Converted staging.json → ./bruno_environments/staging.bru
✅ Converted development.json → ./bruno_environments/development.bru
✅ Converted test_env.json → ./bruno_environments/test_env.bru
✅ Converted qa_env.json → ./bruno_environments/qa_env.bru
✅ Converted sandbox.json → ./bruno_environments/sandbox.bru
✅ Converted integration.json → ./bruno_environments/integration.bru
✅ Converted demo_env.json → ./bruno_environments/demo_env.bru

✨ Done! Converted 10/10 file(s)
```

#### Validator Command

The script can be found here: [validate_bruno_files.py](https://gist.github.com/ashwch/cd87eb1574b1b88d21ddef1508a186f6)

### Command

```bash
$ uv run validate_bruno_files.py ./bruno_environments/
```

### Output

```text
🔍 Validating 10 Bruno file(s)...

✅ demo_env.bru
✅ development.bru
✅ integration.bru
✅ local_dev.bru
✅ performance_test.bru
✅ production.bru
✅ qa_testing.bru
✅ sandbox.bru
✅ staging.bru
✅ user_acceptance.bru

📊 Summary: 10/10 file(s) valid
```

### Request Migration Script

For the actual requests, here's a simple bash script:

```bash
#!/bin/bash
# convert_postman_scripts.sh

# Common replacements
sed -i 's/JSON\.parse(responseBody)/res.getBody()/g' *.bru
sed -i 's/atob(/Buffer.from(/g' *.bru
sed -i 's/pm\.environment\.set(/bru.setEnvVar(/g' *.bru

# Fix dictionary access patterns
sed -i 's/jsonData\["\([^"]*\)"\]/jsonData.\1/g' *.bru
```

**Pro tip**: Run this on a copy first. Some replacements might need manual review, especially if you have complex string patterns.

## Common Migration Patterns

### Response Validation

Add defensive checks when migrating:

```javascript
// Old Postman way (often broke with null responses)
var id = JSON.parse(responseBody)["data"]["id"];

// Better Bruno pattern
var response = res.getBody();
if (response && response.data && response.data.id) {
  bru.setEnvVar("resource_id", response.data.id);
} else {
  console.error("Unexpected response structure:", response);
}
```

### Test Migration

If you have Postman tests:

```javascript
// Postman test
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Bruno test
test("Status code is 200", function () {
    expect(res.getStatus()).to.equal(200);
});
```

## The AI Integration Revolution

Here's where things get exciting. I created a custom Claude [slash command](https://docs.anthropic.com/en/docs/claude-code/slash-commands) that analyzes our Bruno files and generates comprehensive documentation by inspecting our Django codebase.

### The `/bruno-api` Command

Instead of maintaining documentation scripts, we taught Claude to understand our codebase. Here's how the actual command works:

```text
# Custom Claude Command: /bruno-api

When the user types `/bruno-api [bruno-file-path]`, you will:

1. **Parse the Bruno File**
   - Extract the HTTP method, endpoint URL, headers, and body structure
   - Identify authentication requirements (Bearer token, API key, etc.)
   - Note any pre/post-request scripts for context

2. **Reverse Engineer the Backend**
   - Use the endpoint URL to find the Django URL pattern:
     path('api/v2/users/', UserViewSet.as_view())
     re_path(r'^api/v1/reports/(?P<pk>\d+)/$', ReportDetailView.as_view())
   - Locate the corresponding view/viewset class
   - For Django Ninja endpoints, find the router and operation functions

3. **Deep Code Analysis**
   - Extract serializer fields, types, validation rules
   - Identify permission classes and authentication requirements
   - Trace through the view method to understand:
     - Query parameters and filtering
     - Data transformations
     - External service calls
     - Error conditions

4. **Generate Comprehensive Documentation**
   Including:
   - Full API endpoint documentation
   - TypeScript interfaces for request/response
   - React Query hooks with error handling
   - Authentication requirements
   - Business logic notes (caching, rate limits, etc.)
   - Common error scenarios
```

Note: For brevity, we have excluded a lot of details like `allowed-tools`, `Context` etc from the command above. But these and other internal project specific details are present in our `/bruno-api` command.

### How It Analyzes Your Code

The sophistication comes from how Claude connects all the pieces:

```text
# Claude's Analysis Process:

1. Bruno file says: GET /api/v2/analytics/inclusion-scores/
2. Find in urls.py: path('api/v2/analytics/inclusion-scores/', InclusionScoresView.as_view())
3. Find InclusionScoresView class
4. Analyze the get() method:
   - What serializer? InclusionScoresSerializer
   - What permissions? IsAuthenticated + HasAnalyticsAccess
   - What does it do? Aggregates survey data with demographic breakdowns
5. Check serializer fields and validation
6. Find related models and business logic
7. Generate complete, accurate documentation
```

**The magic**: This is more than just brittle script parsing AST. Claude Code understands our code semantically, follows imports, and comprehends business logic and can inspect multiple aspects of an API.

### Real Example Output

**Input:** Simple Bruno file from Postman migration - [see this basic file](https://gist.github.com/ashwch/2a9d05024ac43479782092acbd4eae8f) (just endpoint + auth)

**Command:** `/bruno-api bruno/analytics/user_metrics.bru`

**Output:** Claude analyzes the Django codebase and generates comprehensive documentation. Here's a small sample:

```typescript
// TypeScript Interfaces (auto-generated from Django serializers)
interface UserMetricsResponse {
  count: number;
  next: string | null;
  results: Array<{
    user_id: string;
    email: string;
    last_active: string;
    total_sessions: number;
    sessions_this_month: number;
    avg_session_duration: string;
    status: 'active' | 'inactive';
    role: string;
    department: string | null;
  }>;
}

// React Query Hook (with error handling derived from Django views)
export const useUserMetrics = (companyId: string, params?: UserMetricsParams) => {
  return useQuery({
    queryKey: ['user-metrics', companyId, params],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/v2/companies/${companyId}/user-metrics/`,
        { params }
      );
      return response.data;
    },
    enabled: !!companyId,
    retry: (failureCount, error: any) => {
      // Smart retry logic based on Django view error handling
      if (error?.response?.status === 401 || error?.response?.status === 403) {
        return false;
      }
      return failureCount < 3;
    }
  });
};
```

**This is just a fraction of the output.** [See the complete generated documentation](https://gist.github.com/ashwch/65dc35b651c989355bb924b5bfb09bd8) which includes:

- Complete API documentation with request/response examples
- Comprehensive error handling for all status codes
- Authentication and permission requirements
- TypeScript interfaces for all data structures
- React Query hooks with infinite scrolling support
- Testing examples and integration patterns
- Business logic notes and performance considerations
- Implementation details and database optimization notes

**The key insight:** Claude reads the actual implementation, so the documentation is always accurate. _It can still make mistakes, so it's always critical to review the files and nudge it in right direction_.

### Adapting for Your Framework

This approach works for any framework:

- **Django**: Find views, serializers, permissions
- **Express**: Parse routes, middleware, validators
- **Rails**: Analyze controllers, strong params
- **FastAPI**: Extract Pydantic models, dependencies

## The Unexpected Benefits

### 1. Code Reviews for API Changes

When someone changes an API, reviewers can see it in the PR:

```diff
git diff api/users/create.bru

+ body:json {
+   {
+     "email": "{{email}}",
+     "role": "{{role}}",
+     "department": "{{department}}"  // New field added
+   }
+ }
```

Breaking changes are caught before deployment, not after.

### 2. AI-Powered API Discovery

New and existing team members can ask:
- "Show me all endpoints that return user data"
- "How do I paginate through results?"
- "Generate TypeScript types for the profile endpoint"

Claude reads your Bruno collections and provides accurate answers and vice-versa.

### 3. Documentation That Stays Fresh

Since docs live with code, they're more likely to stay updated. We are working on a pre-commit hook that is going to remind developers to update Bruno files when an API related change is made.

## Getting Your Team Started

### Start Small, Move Fast

We did our entire migration over a weekend, and you can too. Here's what worked for us:

1. **Pick your proof of concept** - Choose one well-used Postman collection
2. **Run the migration scripts** - Use the Python converters linked above
3. **Set up your first AI command** - Start with our `/bruno-api` template
4. **Show, don't tell** - Generate docs for one endpoint and share with the team

### The Aha Moment

The real buy-in happens when developers see:
- Their API changes appearing in PR diffs
- Claude Code generating accurate TypeScript interfaces
- Documentation that actually matches the code
- No more "update Postman" tickets in the backlog

### Practical Next Steps

- **Today**: [Export one Postman collection](https://learning.postman.com/docs/getting-started/importing-and-exporting/exporting-data/), import to Bruno
- **Tomorrow**: Create your first custom Claude command
- **This Week**: Add `.bru` files to your repo and update PR templates
- **Next Sprint**: Deprecate Postman licenses and celebrate the cost savings

### Common Questions We Heard

- "Can QA still use it?" → Yes, Bruno has a UI too (and it's free)
- "What if we need to go back?" → Keep Postman exports for 30 days, but we never looked back

### Creating Your Own AI Commands

Here's a complete example you can adapt:

```markdown
# .claude/commands/bruno-api.md

You are an API documentation expert for our [Framework] application.

When user types /bruno-api [file-path]:

1. Read the Bruno file at the specified path
2. Extract: method, URL, headers, body structure
3. Find the implementation:
   - For Express: Find app.get/post/put in routes/
   - For Django: Find path() in urls.py, then view
   - For Rails: Find route in config/routes.rb
4. Analyze the handler/controller to determine:
   - Required parameters and validation
   - Authentication/authorization 
   - Response structure
   - Error cases
5. Generate documentation including:
   - Clear description of what the endpoint does
   - Request/response examples with real data
   - [Your frontend framework] integration code
   - Common errors and how to handle them

Use our conventions:
- TypeScript for all interfaces
- Include data validation rules
- Show rate limits if applicable
- Note any side effects (emails, webhooks, etc.)
```

**Implementation tip**: Start with one endpoint type (e.g., CRUD operations) and expand from there.

## What This Means for Engineering Teams

The shift from Postman to Bruno in 2025 is really a shift in how we think about API documentation. It's no longer a separate artifact that gets out of sync. It's part of your codebase, reviewed like code, and enhanced by AI.

### Immediate Benefits We Measured

- **API documentation time**: Reduced from days to hours
- **Documentation quality**: Rich Markdown docs with examples, tables, and diagrams (vs. limited formatting options and inconsistent AI-generated docs in Postman)
- **Breaking changes caught**: Significant improvement during code review (from rarely caught to consistently visible in PRs)
- **Team participation**: Entire team can now contribute without needing a Postman seat
- **Onboarding time**: New engineers integrate APIs faster with self-documenting collections and AI-generated examples