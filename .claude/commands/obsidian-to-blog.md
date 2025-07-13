---
allowed-tools: Read, Write, MultiEdit, Glob, Task, TodoWrite
description: Convert Obsidian markdown blog posts to Pelican-ready articles with proper metadata, formatting, and validation
---

# Obsidian to Blog Post Converter

## Usage Examples:
```bash
# Convert an Obsidian note to blog post
/obsidian-to-blog ~/Documents/Synced\ Vault/6\ -\ Full\ Notes/My\ Blog\ Post.md

# Convert with custom slug
/obsidian-to-blog --slug my-custom-slug ~/Documents/path/to/obsidian/note.md

# Dry run - preview the conversion without creating file
/obsidian-to-blog --dry-run ~/Documents/path/to/obsidian/note.md
```

## Context

- Current arguments: `$ARGUMENTS`
- Has --dry-run flag: !`echo "$ARGUMENTS" | grep -q "\-\-dry-run" && echo "YES" || echo "NO"`
- Has --slug flag: !`echo "$ARGUMENTS" | grep -q "\-\-slug" && echo "YES" || echo "NO"`
- Custom slug (if specified): !`echo "$ARGUMENTS" | grep -o "\-\-slug [^ ]*" | cut -d' ' -f2 || echo "None"`
- Input path: !`echo "$ARGUMENTS" | sed 's/--[a-z-]* [^ ]*//g' | sed 's/--[a-z-]*//g' | xargs`

## Your Task

Convert the Obsidian markdown file to a Pelican-compatible blog post by following these steps:

### 1. Read and Parse Obsidian File

- Extract the Obsidian file content
- Identify metadata like Status tags (#adult, #draft, etc.)
- Extract Obsidian tags (lines starting with "Tags:")
- Note the creation date if present
- Extract the main title (usually the first heading or filename)

### 2. Generate Pelican Metadata

Create the required Pelican frontmatter:

```markdown
Title: [Extract from content or filename]
Date: [Today's date in YYYY-MM-DD format]
Modified: [Same as Date]
Category: [Determine from content - Programming, Engineering, Productivity, etc.]
Tags: [Convert Obsidian tags, remove # symbols, add relevant tags]
Slug: [Generate from title or use --slug if provided]
Authors: Ashwini Chaudhary
Summary: [Generate a compelling 1-2 sentence summary]
```

### 3. Process Content

- Remove Obsidian-specific syntax:
  - Status tags (#adult, #draft, etc.)
  - Tags: line
  - Date/time stamps at the beginning
  - Empty lines at the start
- Convert Obsidian links `[[Link]]` to regular markdown if any
- Ensure proper markdown formatting:
  - Fix heading levels (start with ## for sections)
  - Ensure code blocks have language identifiers
  - Fix any Obsidian-specific formatting

### 4. Enhance for Blog

- Ensure the article has a clear introduction
- Add section headings if needed for better structure
- Validate all links work (convert local Obsidian links appropriately)
- Ensure code blocks are properly formatted with language tags
- Keep any quotes, lists, and special formatting intact

### 5. Category Selection

Choose the most appropriate category based on content:
- **Programming**: Technical tutorials, code-focused content, language features
- **Engineering**: Architecture, best practices, team processes, tools
- **Productivity**: Workflow improvements, tool reviews, efficiency tips
- **Career**: Leadership, hiring, professional development
- **Open Source**: OSS contributions, project announcements

### 6. Tag Generation

- Extract all Obsidian tags and clean them (remove #)
- Add relevant technical tags based on content analysis
- Include tool/technology names mentioned prominently
- Keep tags lowercase, use hyphens for multi-word tags
- Aim for 5-10 relevant tags

### 7. Output Generation

If --dry-run flag is present:
- Show the converted content preview
- Display extracted metadata
- List any warnings or suggestions
- DO NOT create the actual file

If --dry-run flag is NOT present:
- Generate slug from title (kebab-case) or use --slug value
- Create file at: `/Users/monty/work/monty/ashwch.github.io/content/articles/[slug].md`
- Save the complete converted content
- Validate the output file

### 8. Validation

After creating the file, verify:
- All required Pelican metadata is present
- No Obsidian-specific syntax remains
- Code blocks have proper language identifiers
- Links are properly formatted
- The summary accurately reflects the content

### Example Conversion

From Obsidian:
```markdown
2025-07-13 14:07

Status: #adult 

Tags: #postman #bruno #api #ai #claude-code

# My Awesome Tool Migration

We moved from Tool A to Tool B...
```

To Pelican:
```markdown
Title: My Awesome Tool Migration
Date: 2025-07-13
Modified: 2025-07-13
Category: Engineering
Tags: postman, bruno, api, ai, claude-code, productivity, tooling
Slug: my-awesome-tool-migration
Authors: Ashwini Chaudhary
Summary: A detailed guide on migrating from Tool A to Tool B, improving our workflow efficiency by 90%.

We moved from Tool A to Tool B...
```

Now, let me process the Obsidian file based on the provided arguments.