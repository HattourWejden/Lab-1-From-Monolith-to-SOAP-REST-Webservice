# Lab 1 - From Monolith to SOAP & REST (Part 1: Monolithic)

## Part 1 : Limitations of the Monolithic Approach
1. **Tight coupling**: UI, business logic, and data access are within the same application/file; changing one part may affect others.
2. **Poor scalability**: You can't scale specific concerns independently (e.g., API vs worker).
3. **Difficult integration**: Other systems cannot easily consume functionality because there is no clear service/API boundary.
4. **Testing pain**: Unit testing is harder because functions depend on shared global state and database connections.
5. **Deployment friction**: Any small change requires redeploying the whole application.
6. **Maintenance & team collaboration**: As the codebase grows it becomes harder for teams to work on separate features without conflicts.

### Part 2: SOAP Webservice (SOA)

*SOAP enforces structure and contracts** through the **WSDL (Web Services Description Language)**, which defines:

*   **Available operations** (methods)
    
*   **Input and output message types**
    
*   **Data types and constraints** (e.g., integers, strings, floats)
    
*   **Endpoint URLs**
    

In contrast, a monolithic script has **no formal contract**, so:

*   Other applications must know the exact function signatures manually
    
*   There is no standard message format
    
*   Changes in the code can break clients silently
    

SOAP + WSDL ensures that any client (web, mobile, or another service) can **discover the service, validate inputs, and consume it reliably** without breaking, providing **stronger interoperability and structure**.