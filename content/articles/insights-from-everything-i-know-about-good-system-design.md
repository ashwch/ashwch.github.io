Title: Insights from "Everything I Know About Good System Design"
Date: 2025-08-17
Category: Development
Tags: system-design, software-architecture, database-design, state-management, performance, best-practices
Slug: insights-from-everything-i-know-about-good-system-design
Authors: Ashwini Chaudhary
Summary: My thoughts and practical experiences applying Sean Goedecke's system design principles - from state management to database schemas, with real-world lessons learned over 10+ years.

> The hard part about software design is state. If you're storing any kind of information for any amount of time, you have a lot of tricky decisions to make about how you save, store and serve it.

I recently read Sean Goedecke's excellent piece on [system design principles](https://www.seangoedecke.com/good-system-design/), and it crystallized many lessons I've learned over 10+ years of building systems. Here are my key takeaways and how they've played out in practice.

---

## Table of Contents

1. [State: The Root of All Complexity](#state-the-root-of-all-complexity)
2. [Database Design: Get the Schema Right](#database-design-get-the-schema-right)
3. [Query Efficiency: Let the Database Work](#query-efficiency-let-the-database-work)
4. [Background Processing: Fast vs. Slow Operations](#background-processing-fast-vs-slow-operations)
5. [Caching: Choose Carefully](#caching-choose-carefully)
6. [Hot Paths: Zero Margin for Error](#hot-paths-zero-margin-for-error)
7. [Logging and Error Handling](#logging-and-error-handling)
8. [Graceful Failure: The Hardest Problem](#graceful-failure-the-hardest-problem)
9. [The Pattern Recognition](#the-pattern-recognition)

---

## State: The Root of All Complexity

State makes everything tricky. The more state we have, the harder it becomes to reason about our systems and keep track of responsibilities.

On the flip side, statelessness relieves us of worrying about systems getting "stuck" or needing complex guardrails to prevent corruption.

> You should try and minimize the amount of stateful components in any system.

> What this means in practice is having one service that knows about the state - i.e. it talks to a database - and other services that do stateless things. Avoid having five different services all write to the same table.

I'll admit this isn't something I actively think about - I might be doing it unconsciously in some cases and missing it entirely in others. But I want to keep an eye on this pattern in future projects.

## Database Design: Get the Schema Right

> Schema design should be flexible, because once you have thousands or millions of records, it can be an enormous pain to change the schema.
> However, if you make it too flexible (e.g. by sticking everything in a "value" JSON column, or using "keys" and "values" tables to track arbitrary data) you load a ton of complexity into the application code (and likely buy some very awkward performance constraints).

I've always spent significant time on database design when building new systems, and it's consistently paid off. The JSON trap is real - while convenient initially, JSON fields create several problems:

- Hard to query effectively
- Difficult to enforce schemas
- Serialization/deserialization overhead
- Network transfer costs for large payloads
- Additional validation complexity

That said, I've found JSON fields useful for storing external API payloads and validation errors - places where the structure truly varies.

### Index Strategy

> If you expect your table to ever be more than a few rows, you should put indexes on it.

I think the author didn't intend it, but **index as you go**. If your table isn't showing slow queries yet, don't index prematurely. You can always add indices later and optimize them based on actual query patterns.

I'm a big fan of PostgreSQL's `explain analyze` - and with AI tools, analyzing query plans has become even more accessible.

## Query Efficiency: Let the Database Work

> When querying the database, _query the database_. It's almost always more efficient to get the database to do the work than to do it yourself. For instance, if you need data from multiple tables, `JOIN` them instead of making separate queries and stitching them together in-memory. Particularly if you're using an ORM, beware accidentally making queries in an inner loop. That's an easy way to turn a `select id, name from table` to a `select id from table` and a hundred `select name from table where id = ?`.

As a longtime Django user who's been reviewing Django code for 10+ years, I've seen the N+1 query problem countless times. It's crucial to educate your team on ORM fundamentals and maintain documentation of good vs. bad practices.

Having a central document helps during code reviews - it's hard to repeatedly explain the "why" with the same depth. A shared resource makes linking to best practices much easier.

## Background Processing: Fast vs. Slow Operations

The goal is a fast request-response cycle for the best user experience. Operations that can't be completed quickly should move to background processing, with users notified when complete.

This seems obvious, but determining what belongs in the background requires careful consideration of user expectations and system constraints.

## Caching: Choose Carefully

Be selective about what and when to cache. Otherwise, you'll face the much harder problem of cache invalidation. The best solution is reducing the number of places using cache.

Cache invalidation remains one of the hardest problems in computer science for good reason.

## Hot Paths: Zero Margin for Error

I define hot paths as system components where downtime significantly affects our SLA - critical numbers, authentication, or features that directly impact business and users.

These systems require extra care:
- World-class unit tests and coverage
- Attention to unhappy paths
- More conservative change management

Take Instagram: it's more important for signed-in users to see their feed than for signup to work perfectly.

## Logging and Error Handling

Beyond traditional logging, we utilize logs in unit tests to ensure they're not removed carelessly during updates. This makes log changes visible during code review.

We also return custom error codes with responses - they help identify issues without log diving and assist both customers and developers debugging problems.

For critical errors sent to monitoring tools like Sentry, we use custom exception names to quickly spot issue locations based on error messages.

## Graceful Failure: The Hardest Problem

This ties back to state management. Building resilient state machines requires balancing when to fail, retry frequency, state resets, and maintaining manageable state complexity.

It's one of the trickiest aspects of system design - fighting between reliability and simplicity.

## The Pattern Recognition

After years of building systems, these principles become pattern recognition. The key is being intentional about applying them rather than hoping they happen by accident.

Sean's post does an excellent job distilling complex system design into actionable principles. The challenge is remembering to apply them when you're deep in implementation details.

---

What patterns have you noticed in your own system design work? I'd love to hear about principles that have served you well over time.