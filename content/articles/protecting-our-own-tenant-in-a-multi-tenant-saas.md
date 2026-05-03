Title: Protecting Our Own Tenant in a Multi-Tenant SaaS
Date: 2025-11-24
Modified: 2025-11-24
Category: Security, Engineering, SaaS
Tags: security, django, postgres, rls, aws, multi-tenant, saas, optimo, diversio, permissions, production, iam
Slug: protecting-our-own-tenant-in-a-multi-tenant-saas
Authors: Ashwini Chaudhary
Summary: How we treat Diversio's own tenant inside Optimo as the hardest one to reach, using layered controls across Django admin, approvals, Postgres RLS, IAM and automation.

> If your own company is a tenant in your own product, it should be the hardest one to access, not the easiest.

At [Diversio](https://diversio.com), one of the products we build is [Optimo](https://optimoteams.com), a multi-tenant SaaS that helps HR and people teams work with sensitive employee and organizational data.

Most Optimo organizations belong to customers.

One belongs to us.

That internal Diversio org inside Optimo holds our own employee and company data. It lives in the same production cluster as customer tenants, and our engineers and Client Success team use the same product surfaces to support both, always through per-tenant and role-based guardrails.

Customer orgs already have their own access boundaries; this post is about holding our own org to an even higher bar so it is the hardest one to reach, not the easiest.

Even with those existing guardrails, it is easy for internal tooling to drift toward a de facto "god mode" for your own org if you never make the extra constraints explicit. We wanted to push in the opposite direction. We wanted everyone at Diversio to be comfortable with how their data is handled, while still letting a very small engineering team move quickly for customers.

This post walks through how we got there.

---

## Table of Contents

1. [What you'll learn](#what-youll-learn)
2. [Why our own org is special](#why-our-own-org-is-special)
3. [Layer 1: An org-scoped admin mixin](#layer-1-an-org-scoped-admin-mixin)
4. [Layer 2: A TOTP-gated workflow for sensitive access](#layer-2-a-totp-gated-workflow-for-sensitive-access)
5. [Layer 3: Postgres RLS and the sensitive flag](#layer-3-postgres-rls-and-the-sensitive-flag)
6. [Layer 4: IAM and support shells](#layer-4-iam-and-support-shells)
7. [Automation and a five-person team](#automation-and-a-five-person-team)
8. [Gaps and future work](#gaps-and-future-work)
9. [The bottom line](#the-bottom-line)

---

## What you'll learn

By the end of this post, you will see how to:

- Treat your own company's tenant as the hardest one to reach in a multi-tenant SaaS.
- Use an org-scoped admin mixin to get "row-level security" at the application layer.
- Wrap sensitive access behind a small TOTP-gated workflow instead of ad-hoc toggles.
- Lean on Postgres Row-Level Security (RLS) and a single support-shell role to protect production data.
- Use CI to keep your RLS and access model from silently drifting.
- Get all of this working with a five-person engineering team without grinding development to a halt.

If you are building a multi-tenant application and your own company is one of the tenants, this post gives you a concrete set of patterns you can reuse or adapt.

---

## Why our own org is special

When we say "our own org", we mean the internal Diversio organization that lives alongside customer orgs inside Optimo.

It is special for a few reasons:

- It includes our own employee data and internal company information.
- It exercises almost every feature in Optimo, often before customers see it.
- It is the easiest tenant for us to accidentally treat as "less important", because we are so close to it.

This pattern is not unique to us. GitHub runs on GitHub, Slack lives inside Slack, and Stripe’s teams build and operate on top of their own payments APIs and tools. Claude Code is another good example: a lot of what makes it feel sharp comes from Anthropic dogfooding it heavily[^dogfood], and we lean on it in our own repos too. Using your own tools at full blast is one of the fastest ways to find sharp edges before customers do.

Optimo is the same. Our own org is where we try new workflows, push edge cases and shortcut a lot of “demo tenant” friction. That is great for product quality, but it also means the easiest tenant for us to poke at is the one tenant we should be most careful with.

We wanted to set a very simple rule:

> If a control is good enough for a sensitive customer, it should apply to Diversio too.

At the same time, we did not want a giant "break everything" toggle in one admin screen that quietly bypassed all of this for engineers on call.

The result is a layered design:

1. A clear notion of which organizations each admin may see at the application layer.
2. A small, TOTP-gated workflow to grant and remove sensitive access.
3. Postgres RLS that treats sensitive orgs as a first-class concept.
4. IAM and support shells that default engineers into safe roles.
5. Automation that keeps all of these in sync as the system changes.

The rest of this post goes layer by layer.

---

## Layer 1: An org-scoped admin mixin

Most internal users at Diversio interact with data through Django admin and a handful of internal consoles. That is where we started.

We already had the usual multi-tenant pieces:

- An `Organization` model.
- Internal staff users who can act on behalf of organizations.
- A boolean flag that means "this organization is sensitive".

The problem was that each Django admin class had to remember to do the right thing. It is easy to get one view right, then forget the filter on another.

So we pulled the logic into a reusable organization-scoped admin mixin (internally, `OptimoOrgScopedAdminMixin`).

At a high level, every staff user has:

- A global profile (are they active staff, what kind of staff).
- Per-org assignments (which customers or regions they are responsible for).
- A flag indicating whether they are allowed to see any sensitive orgs at all.

A central helper answers a single question:

```python
def get_allowed_org_ids(user) -> set[int]:
    # Look at profile, per-org permissions and the sensitive flag.
    # Return the set of organization IDs this user may see.
    ...
```

The admin mixin uses this helper to:

- Filter list views down to the organizations you are allowed to see.
- Enforce object-level permissions ("can I view, change or delete this row").
- Narrow foreign keys and dropdowns so you cannot accidentally link records to orgs you do not have access to.

A simplified version looks like this:

```python
class OrgScopedAdmin(ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        allowed = get_allowed_org_ids(request.user)
        return qs.filter(organization_id__in=allowed)

    def has_view_permission(self, request, obj=None):
        base = super().has_view_permission(request, obj)
        if not base or obj is None:
            return base
        return obj.organization_id in get_allowed_org_ids(request.user)
```

Two important choices here:

- Sensitive orgs (including Diversio) are excluded by default, even for superusers.
- Admin views opt in to the mixin and get the same behaviour, instead of reinventing access rules one screen at a time.

For an engineer with strong customer-facing permissions:

- Django admin is still powerful for the customer orgs they are assigned to.
- The Diversio org simply does not show up unless a separate process has granted that level of access.

This is our first layer of "row-level security": an application-level filter baked into admin, not an afterthought in each view.

---

## Layer 2: A TOTP-gated workflow for sensitive access

The admin mixin enforces "what you can see" for a given profile.

The next question is: how does someone get a profile that is allowed to see the Diversio org at all?

We knew what we did not want:

- A checkbox in Django admin that anyone with enough permissions could toggle.
- A permanent "god mode" role that people forget they are still holding.

Instead, we built a small, TOTP-gated workflow.

Each staff profile has a boolean that means:

> This person may see sensitive orgs like Diversio, in addition to their normal org assignments.

That boolean is visible in admin, but it is read-only. The only way to change it is a CLI command that:

- Takes a target user.
- Takes a TOTP code from an approver (CEO, CTO or a small set of delegates).
- Logs who did what and when.

In pseudocode:

```python
def require_sensitive_approval(code: str) -> None:
    if not verify_totp(code):  # shared helper wired to env secrets
        raise ApprovalError("Invalid TOTP code")


def enable_sensitive_access(staff_user, code: str) -> None:
    require_sensitive_approval(code)
    staff_user.can_see_sensitive_orgs = True
    staff_user.save(update_fields=["can_see_sensitive_orgs"])
```

The outcome looks like this in practice:

- Sensitive access is rare and is usually time-boxed to a specific investigation.
- It is deliberate: someone with real authority has to approve it with a physical device.
- It is auditable: we can answer "who could see the Diversio org in April" without guessing.

This is the human-side guardrail that complements the org-scoped admin mixin.

---

## Layer 3: Postgres RLS and the sensitive flag

Application-level scoping and TOTP workflows are necessary, but not sufficient. Engineers also work close to the database: SQL shells, diagnostics, ad-hoc queries and migrations.

We wanted Postgres itself to agree that the Diversio org is special.

We do two things here.

### 3.1 Guard the sensitive flag itself

First, we treat the "this org is sensitive" flag as something you do not get to flip casually.

- Normal application roles and ad-hoc DB connections cannot change it.
- Only a narrow path, tied to the TOTP-gated CLI, can set or clear it.
- The database checks the current role and a session variable before allowing updates to that column.

The goal is simple:

- Nobody "experimenting" in a production shell can quietly downgrade the Diversio org from `is_sensitive = TRUE` to `FALSE`.
- Even if a bug slips through at the app layer, the database is still able to say "no" on the one write that really matters.

### 3.2 Postgres RLS for support shells

The second piece is Postgres Row-Level Security (RLS), which we apply to a dedicated support database role, the role engineers use in our production support shells.

For that support role, RLS policies enforce:

- On org-scoped tables, queries only see rows where the organization is not sensitive.
- Rows belonging to sensitive orgs (including Diversio) are filtered out by the database itself.
- These rules apply to both reads and writes.

In simplified SQL:

```sql
ALTER TABLE org_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY support_only_non_sensitive
  ON org_events
  FOR ALL
  TO support_shell_role
  USING (
    organization_id IN (
      SELECT id
      FROM organizations
      WHERE is_sensitive = FALSE
    )
  );
```

If you connect to production using the support shell and run:

```sql
SELECT * FROM org_events
WHERE organization_id = (
  SELECT id FROM organizations WHERE name = 'Diversio'
);
```

Postgres itself refuses to show those rows to the `support_shell_role`, regardless of what the application code might have done.

### 3.3 An RLS registry and CI checks

We have a lot of org-scoped tables in Optimo:

- Some with a direct `organization_id` column.
- Some where the org needs to be derived via a join (through a user, an employee, a workspace and so on).

Managing RLS for all of them by hand is a great way to make mistakes.

So we maintain a small Python "registry" that lists:

- Which tables are org-scoped.
- How to determine the organization for each table.
- Which tables are intentionally excluded.

On top of that registry, we have a management command that:

- Enables RLS on those tables.
- Ensures policies exist for the support role.
- Creates a helper function like `org_is_not_sensitive(org_id uuid)` for `USING` and `WITH CHECK` clauses.
- Scans the schema for any new org-scoped tables that are not in the registry yet.
- Fails loudly if it finds gaps.

We run this command automatically in CircleCI:

- Apply migrations to a fresh database.
- Run the RLS command in "apply plus verify" mode.
- If someone adds an org-scoped table and forgets to update the registry, the build fails.

Conceptually, the CI step looks like this:

```yaml
- run:
    name: Validate support-shell RLS
    command: |
      python manage.py migrate --noinput
      python manage.py check_support_shell_rls --apply --verbosity 2
```

RLS becomes an executable spec, not a fragile manual checklist.

---

## Layer 4: IAM and support shells that default to safe

The final layer is how we actually connect to production.

Like many teams, we used to have engineers with:

- Broad AWS permissions.
- The ability to run `ecs exec` into production containers.
- Access to secrets wired to powerful database roles.

That is convenient, but it does not align with "the Diversio org should be the hardest tenant to reach".

We reshaped things so that sensitive power is separated and explicit.

### 4.1 Sensitive secrets are separated

Anything that directly powers sensitive workflows, for example:

- Special database URLs.
- TOTP secrets.
- Break-glass admin credentials.

lives in its own secret, encrypted under a dedicated KMS key. Only specific permission sets and automation roles can read it.

### 4.2 Permission sets map to real personas

We distinguish a normal "production engineer" persona from a "break-glass administrator".

The normal production role:

- Cannot talk directly to the main database role.
- Cannot read master database secrets.
- Cannot read sensitive secrets.
- Can still manage non-sensitive app configuration and run diagnostics.

### 4.3 Support shells are the default

Engineers connect to production via a dedicated support-shell service that:

- Runs the same Optimo container image as the main app.
- Uses the restricted support database role by default.
- Is wired so that a normal production engineer always lands in a support shell, not on a fully privileged backend container.

A small wrapper script ties it together:

```bash
permission_set=$(detect_aws_permission_set)

if [ "$permission_set" = "ProdEngineer" ]; then
  target_service="support-shell"
else
  target_service="backend"  # break-glass roles only
fi

open_ecs_exec_shell "$target_service"
```

If the support-shell configuration is missing or broken, the script refuses to open a shell instead of silently falling back to something more powerful.

Combined with RLS, this gives us:

- A realistic production shell for debugging customer issues.
- A database that still hides rows for the Diversio org from the support role.
- A clear, auditable path to more power when it is genuinely needed.

---

## Automation and a five-person team

At this point, it is fair to ask:

> Is this too much machinery for a five-person engineering team?

It would be, if it were all manual.

What makes it work is that the moving parts share a few patterns:

- One admin mixin for org scoping, reused everywhere.
- One TOTP-gated path for sensitive access, instead of scattered toggles.
- One RLS registry and command that define what the database should enforce.
- One CI step that runs migrations, bootstraps RLS and fails when something drifts.

The extra work happens once, up front. After that:

- New admin views inherit the mixin and automatically respect org scoping.
- New engineers follow the same shell story and get the same protections.
- New org-scoped tables are caught by the RLS command if we forget to register them.

The system enforces the policy for us, instead of us trying to remember every rule in our heads.

---

## Gaps and future work

We are happy with the direction, but this is not "done".

Some gaps we have deliberately left open for future iterations:

- **RLS mostly protects the support role today.**  
  We would like to extend RLS to more roles and tables where it makes sense, without tanking performance or complicating migrations.

- **Many read paths still lean on application logic.**  
  The admin mixin does a lot, and the database does a lot for support shells, but other read paths still rely on Django-level scoping. We would like more database-side guardrails around the most sensitive slices of the Diversio org.

- **Sensitive access observability is basic.**  
  We log the right events and can reconstruct them, but we would like:
  - A small dashboard that graphs sensitive access over time.
  - Simple alerts when approvals spike or come from unexpected places.

- **Approvals are very CLI-shaped.**  
  The TOTP flow is fine for engineers, less so for non-engineers. A small internal UI for approvers ("who is asking to see Diversio, why, and for how long") would make this much more approachable.

- **We do not "game day" this enough.**  
  We test the pieces individually. We would like regular drills where we intentionally try to break assumptions about the Diversio org in a safe environment and see how the system responds.

These are good problems to have. They are the kind of problems you get to think about only after you have built the basics.

---

## The bottom line

Letting your own company be a tenant in your own product is a great dogfooding story: your own team runs real workflows through the product every day. It is also a serious security challenge.

Our approach at Diversio has been to:

- Treat the Diversio org as the most demanding customer we have.
- Give the application a clear notion of which orgs each admin may see, via an org-scoped mixin.
- Give the database a clear notion of which rows each role may see, via RLS and a registry.
- Let CI and automation keep those contracts honest as Optimo evolves.
- Build human workflows (approvals, TOTP) into the design from the start.

The key point is not that we use Django or Postgres or AWS specifically. The key point is that we use layers:

- UI and admin behaviour.
- Approval workflows.
- Database policies.
- Cloud IAM and shell tooling.
- Automation to glue it together.

Together, these give us something stronger than "trust us, we will be careful" and they do it in a way that a small, focused team can maintain while still shipping features.

*Thanks to [Ashish Siwal](https://www.linkedin.com/in/ashishsiwal/) for reviewing this post and helping solidify the implementation.*

[^dogfood]: "Dogfooding" just means using your own product internally for real, day-to-day work, so you hit the same pain points and edge cases your customers do.
