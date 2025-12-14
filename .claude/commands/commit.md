# Generate Commit Message

You are helping to generate a conventional commit message based on the current git changes.

## Your Tasks

1. **Analyze Git Changes:**
   - Run `git status` to see staged/unstaged files
   - Run `git diff --stat` to see change statistics
   - Run `git diff --cached` if files are staged, otherwise `git diff`
   - Understand what was changed and why

2. **Detect Commit Type:**
   Based on the files changed, determine the appropriate type:
   - `feat` - New features or functionality, new migrations
   - `fix` - Bug fixes
   - `refactor` - Code refactoring without functionality changes
   - `chore` - Configuration, infrastructure, dependencies
   - `docs` - Documentation only changes
   - `test` - Test changes only
   - `perf` - Performance improvements
   - `style` - Code styling/formatting only

3. **Generate Commit Message:**

   Use this exact format:
   ```
   type: short description (max 50 chars)

   2-3 sentences explaining why this change is beneficial, what problem it solves,
   or what value it provides to the project. Focus on the "why" rather than the "what".

   Changes:
   - Specific change 1
   - Specific change 2
   - Specific change 3
   - etc.
   ```

4. **Present to User:**
   - Show the generated commit message in a code block
   - Briefly explain your reasoning for the type selection
   - Ask if the user wants to:
     - Stage all files (if not staged): `git add -A`
     - Create the commit: `git commit -m "..."`
     - Modify the message first

## Guidelines

- **Headline**: Must be under 50 characters, start with type prefix
- **Description**: 2-3 complete sentences explaining the benefit/reason
- **Changes list**: Be specific about what files/features were modified
- **Tone**: Professional and concise
- **Focus**: Why the change matters, not just what changed

## Example

For authentication changes:
```
feat: add username-based authentication

This change improves security by allowing users to choose memorable usernames
instead of exposing email addresses in the login process. It also provides
better user privacy and follows common authentication patterns.

Changes:
- Add username field to User entity with unique constraint
- Create migration for username column
- Update security config to use username for authentication
- Change login form from email to username input
- Update user creation command to require username
```

## Important Notes

- Do NOT review git log history - use the standard conventional commit types
- Keep headline concise and action-oriented
- In the description, focus on benefits and reasoning
- List all significant changes in the Changes section
- Use present tense ("Add" not "Added")
