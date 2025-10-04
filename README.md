# Lab 1 - From Monolith to SOAP & REST (Part 1: Monolithic)

## Limitations of the Monolithic Approach
1. **Tight coupling**: UI, business logic, and data access are within the same application/file; changing one part may affect others.
2. **Poor scalability**: You can't scale specific concerns independently (e.g., API vs worker).
3. **Difficult integration**: Other systems cannot easily consume functionality because there is no clear service/API boundary.
4. **Testing pain**: Unit testing is harder because functions depend on shared global state and database connections.
5. **Deployment friction**: Any small change requires redeploying the whole application.
6. **Maintenance & team collaboration**: As the codebase grows it becomes harder for teams to work on separate features without conflicts.


