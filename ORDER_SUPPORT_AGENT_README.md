# Order & Delivery Support Agent

An AI-powered customer support agent for handling order and delivery queries using LLM-based reasoning, tool calling, and customer-scoped backend operations.

The system uses LangGraph to orchestrate an agent that can understand a customer's natural-language request, select the appropriate backend tool, retrieve customer-specific information, perform multi-step operations, and generate a final response.

> **Current Status:** Working Proof of Concept (POC)

---

## 1. Project Overview

Traditional customer support systems usually depend on fixed menus, predefined workflows, or human agents to retrieve order and delivery information.

This project explores an agentic approach where a customer can interact with the system using natural language.

For example:

> "Where is my order ORD123?"

The agent can determine that shipment information is required, invoke the appropriate tool, retrieve the tracking information, and generate a response.

Similarly:

> "Can I cancel my order ORD200?"

The agent can retrieve the order details, check its current status, and determine whether the cancellation operation should be performed.

The current implementation focuses on demonstrating the core agentic workflow using LangGraph, LangChain tools, Gemini 2.5 Flash, and FastAPI.

---

## 2. Problem Statement

Customer support systems need to handle multiple types of requests such as:

- Order status
- Shipment tracking
- Delivery information
- Order cancellation
- Ticket creation
- Customer-specific information retrieval

A simple chatbot can understand the user's message, but it cannot safely perform backend operations without controlled access to business systems.

The main challenge is:

> How can we build an AI agent that understands natural-language customer requests, selects the correct backend operation, retrieves only authorized customer data, and performs actions while keeping business logic and security outside the LLM?

---

## 3. Objectives

The project aims to build an agent that can:

- Understand natural-language customer requests
- Identify the required operation
- Select appropriate backend tools
- Execute tools through a controlled interface
- Retrieve customer-specific order information
- Retrieve shipment information
- Handle multi-step tool-calling workflows
- Maintain customer data isolation
- Return a natural-language response
- Expose the agent through an API

---

## 4. Current Architecture

```text
                         Customer
                            |
                            v
                     FastAPI /chat
                            |
                            v
                     LangGraph Agent
                            |
                            v
                    Gemini 2.5 Flash
                            |
                    Tool required?
                       /         \
                     YES          NO
                      |            |
                      v            v
                  Tool Node    Final Answer
                      |
                      v
              Customer-Scoped Tool
                      |
                      v
                 Mock Database
                      |
                      v
                 Tool Result
                      |
                      v
                Agent Node
                      |
              More tools needed?
                  /        \
                YES         NO
                 |           |
                 v           v
              Tool Node   Final Answer
```

The current repository implements a LangGraph `StateGraph` containing an agent node, tool node, and conditional routing that allows the agent to continue calling tools until it has enough information to produce a final response.

---

## 5. Agent Workflow

```text
User Request
     |
     v
Understand Intent
     |
     v
Determine Required Tool
     |
     v
Execute Tool
     |
     v
Observe Tool Result
     |
     v
Need More Information?
   /           \
 YES           NO
  |             |
  v             v
Another Tool  Final Answer
```

This follows an agentic Reason → Act → Observe cycle.

The LLM is responsible for interpreting the request and deciding which available tool should be used.

The actual operation is performed by Python tools rather than by the LLM itself.

---

## 6. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| LLM | Gemini 2.5 Flash |
| Agent Framework | LangGraph |
| Tool Framework | LangChain |
| Backend API | FastAPI |
| Current Database | In-memory mock store |
| Planned Database | PostgreSQL |
| Shipment Tracking | Planned AfterShip integration |
| Demo Interface | CLI / Streamlit |
| Frontend | Planned |
| Memory | Planned Redis / Database |
| Authentication | Planned |

---

## 7. Current Implementation

### 7.1 LangGraph Agent

The agent is implemented using a LangGraph `StateGraph`.

The graph contains:

- Agent node
- Tool node
- Conditional routing
- Iterative tool-calling loop

The agent can call a tool, receive the result, and continue reasoning instead of being restricted to a single tool call.

### 7.2 LangChain Tools

Backend operations are exposed to the LLM as LangChain tools.

Examples include operations for:

- Retrieving orders
- Checking shipment information
- Retrieving customer tickets
- Requesting cancellation

The LLM does not directly access the database.

```text
LLM
 |
 | tool call
 v
LangChain Tool
 |
 v
Backend / Database
 |
 v
Tool Result
 |
 v
LLM
```

This creates a controlled interface between the LLM and backend operations.

---

## 8. Customer Data Isolation

One of the important design decisions is customer-scoped tools.

Tools are created for a specific customer context instead of allowing the model to freely provide an arbitrary customer ID when accessing customer data.

```text
Authenticated Customer
        |
        v
   customer_id
        |
        v
Create customer-scoped tools
        |
        v
       LLM
        |
        v
Tool request
        |
        v
Database access restricted
to that customer
```

The LLM is not treated as the security boundary.

The application/tool layer should enforce authorization.

> Note: The current POC does not yet implement a real authentication layer. Customer identity is currently supplied through the request.

---

## 9. Current Data Model

The current POC uses an in-memory mock store representing entities such as:

```text
Customers
Orders
Shipments
Tickets
```

The mock data is intentionally used to demonstrate the agent workflow without requiring a production database.

---

## 10. Example Interaction

### User

```text
Where is my order ORD123?
```

### Agent Workflow

```text
1. Understand request
2. Identify order
3. Retrieve order information
4. Retrieve shipment information
5. Inspect tracking status
6. Generate response
```

---

# 11. Main Problems To Implement

The current implementation is a POC. The following are the major engineering problems that should be addressed.

## 11.1 Real Authentication

### Current Problem

The current API accepts a customer ID directly in the request.

```json
{
  "customer_id": "C1024",
  "message": "Where is my order?"
}
```

This means the identity is not yet established through a real authentication mechanism.

### Implementation

Add:

```text
Login
  |
  v
Authentication
  |
  v
Verified Identity
  |
  v
Customer ID
  |
  v
Customer-scoped tools
```

Possible approaches:

- JWT authentication
- Session-based authentication
- OAuth2

The customer ID should come from the verified identity rather than an arbitrary request field.

---

## 11.2 Replace Mock Database With PostgreSQL

### Current Problem

The project currently uses an in-memory mock store.

### Implementation

Replace:

```text
mock_data.py
```

with:

```text
PostgreSQL
    |
SQLAlchemy
    |
CRUD / Repository Layer
    |
LangChain Tools
```

Suggested tables:

```text
customers
orders
shipments
tickets
```

---

## 11.3 Real Shipment Tracking

### Current Problem

Shipment tracking is currently based on sample/mock data.

### Implementation

Integrate a shipment tracking provider such as AfterShip.

```text
Customer Request
      |
      v
Order Lookup
      |
      v
Tracking Number
      |
      v
Tracking API
      |
      v
Latest Tracking Status
      |
      v
LLM Response
```

The integration should handle:

- API failures
- Invalid tracking numbers
- Timeouts
- Missing tracking information
- Rate limits

---

## 11.4 Persistent Conversation Memory

### Current Problem

The system does not currently provide persistent conversation memory.

### Implementation

Use:

```text
Redis
```

or:

```text
PostgreSQL conversations table
```

Workflow:

```text
User
 |
 v
Conversation ID
 |
 v
Retrieve History
 |
 v
LangGraph
 |
 v
Store New Messages
```

Memory should be scoped to the appropriate customer and conversation.

---

## 11.5 Deterministic Business Rules

The LLM should not be responsible for deciding business rules.

For example:

```text
User:
Cancel my order ORD200.
```

The LLM can request:

```text
request_cancellation(order_id="ORD200")
```

But the backend should determine:

```text
Does order exist?
        |
Is it owned by customer?
        |
Is cancellation allowed?
        |
Is order already shipped?
        |
Is payment already processed?
        |
Is cancellation permitted?
```

Then:

```text
Allowed  -> Continue
Denied   -> Return reason
```

Business rules should be implemented deterministically in backend code.

---

## 11.6 Human-in-the-Loop Cancellation

Cancellation is a state-changing operation.

A safer workflow is:

```text
User
 |
 v
Agent
 |
 v
Cancellation Request
 |
 v
Authorization
 |
 v
Business Validation
 |
 v
Human Approval
 |
 +---- Rejected
 |
 +---- Approved
          |
          v
      Cancel Order
```

This prevents the LLM from directly controlling sensitive state changes.

---

## 11.7 Ticket Escalation

The agent should be able to escalate issues that cannot be safely resolved automatically.

```text
Customer Problem
      |
      v
Can Agent Resolve?
   /          \
 YES           NO
  |             |
  v             v
Answer       Create Ticket
                |
                v
          Human Support
```

Potential escalation cases:

- Payment disputes
- Delivery failures
- Damaged products
- Refund disputes
- Missing packages
- Explicit human-support requests

---

## 11.8 RAG / Policy Retrieval

The current system does not include policy retrieval.

A production-oriented system can retrieve controlled support policies before answering policy-dependent questions.

```text
User Request
      |
      v
Retrieve Policy
      |
      v
Check Order State
      |
      v
Apply Policy
      |
      v
Generate Response
```

Potential documents:

- Cancellation Policy
- Refund Policy
- Shipping Policy
- Return Policy
- Delivery SLA
- Customer Support Guidelines

---

## 11.9 Observability

The system should record the important stages of each agent request.

```text
Request ID
Customer ID
Conversation ID
User Query
Selected Tool
Tool Arguments
Tool Execution Time
Tool Result
LLM Response Time
Errors
Final Response
```

This makes incorrect agent behavior easier to debug.

---

## 11.10 Agent Evaluation

Create an evaluation dataset containing:

```text
User Query
Expected Intent
Expected Tool
Expected Arguments
Expected Result
Expected Final Response
```

Example:

| Query | Expected Tool |
|---|---|
| Where is my order? | get_order |
| Track my shipment | get_tracking_status |
| Can I cancel my order? | request_cancellation |
| Show my support tickets | get_customer_tickets |

Important metrics:

- Tool-selection accuracy
- Argument accuracy
- Customer-isolation violations
- Response correctness
- Latency
- Failure rate
- Hallucination rate

---

## 11.11 Error Handling

The agent should gracefully handle:

### LLM failure

```text
LLM unavailable
     |
     v
Retry / fallback
```

### Database failure

```text
Database unavailable
     |
     v
Controlled error
```

### External API failure

```text
Tracking API unavailable
     |
     v
Do not fabricate tracking information
```

### Invalid tool arguments

```text
Invalid order ID
      |
      v
Validation
      |
      v
Ask user for clarification
```

---

## 11.12 Reliability

The API should eventually include:

- Request rate limiting
- Timeouts
- Retry policies
- Circuit breakers for external APIs
- Idempotency for state-changing operations
- Structured logging
- Agent loop limits

For example, cancellation should not execute twice because of a network retry.

---

# 12. Recommended Implementation Roadmap

## Phase 1 — Current POC

- [x] LangGraph agent
- [x] Gemini 2.5 Flash
- [x] LangChain tools
- [x] Tool calling
- [x] Customer-scoped tools
- [x] FastAPI endpoint
- [x] Mock database
- [x] CLI demo

## Phase 2 — Backend Foundation

- [ ] PostgreSQL
- [ ] SQLAlchemy
- [ ] Repository / CRUD layer
- [ ] Database migrations
- [ ] Data validation
- [ ] Better error handling

## Phase 3 — Security

- [ ] Authentication
- [ ] JWT/session management
- [ ] Authorization
- [ ] Verified customer identity
- [ ] Tool-level authorization
- [ ] Audit logging

## Phase 4 — Real Integrations

- [ ] Shipment tracking API
- [ ] External API error handling
- [ ] Timeouts
- [ ] Retry strategy

## Phase 5 — Agent Reliability

- [ ] Persistent memory
- [ ] Tool validation
- [ ] Business-rule validation
- [ ] Retry limits
- [ ] Loop protection
- [ ] Tool-call logging
- [ ] Agent evaluation

## Phase 6 — RAG

- [ ] Policy document ingestion
- [ ] Embeddings
- [ ] Vector database
- [ ] Policy retrieval
- [ ] Source tracking

## Phase 7 — Human-in-the-Loop

- [ ] Cancellation approval
- [ ] Ticket escalation
- [ ] Human support queue
- [ ] Approval/rejection workflow
- [ ] Customer notification

## Phase 8 — Production UI

- [ ] Customer login
- [ ] Chat interface
- [ ] Order history
- [ ] Shipment tracking
- [ ] Ticket history
- [ ] Support dashboard
- [ ] Human escalation interface

---

# 13. Production-Oriented Architecture

```text
                    Customer
                       |
                       v
                 Web / Mobile UI
                       |
                       v
                 Authentication
                       |
                       v
                    FastAPI
                       |
                       v
                 LangGraph Agent
                       |
             +---------+---------+
             |                   |
             v                   v
          Gemini              Memory
             |                Redis/DB
             |
             v
        Tool Selection
             |
     +-------+-------+----------------+
     |       |       |                |
     v       v       v                v
   Order   Tracking Tickets       Policy RAG
   Tool      Tool     Tool
     |       |       |
     +-------+-------+
             |
             v
          Services
             |
      +------+------+
      |             |
      v             v
 PostgreSQL    External APIs
```

---

# 14. Key Design Principle

The project separates LLM responsibilities from deterministic backend responsibilities.

```text
LLM
=
Intent understanding
+
Tool selection
+
Natural-language response

Backend
=
Authentication
+
Authorization
+
Business rules
+
Data access
+
State changes

Tools
=
Controlled interface between LLM and backend
```

The LLM should not be treated as the final security or authorization boundary.

---

# 15. Current Limitations

The current implementation is intentionally a POC.

Current limitations include:

- In-memory database
- No real authentication
- No RBAC implementation
- Request-supplied customer ID
- Mock shipment tracking
- No real tracking API
- No persistent conversation memory
- No RAG/policy retrieval
- No production frontend
- No ticket escalation UI
- No human approval workflow
- Limited observability
- Limited automated evaluation

These are the main areas to address when moving the project toward a production-oriented implementation.

---

# 16. Future Goal

The project should evolve from:

```text
LLM + Mock Data + Tools
```

into:

```text
Authenticated User
        |
        v
Production API
        |
        v
LangGraph Agent
        |
        +---- PostgreSQL
        |
        +---- Shipment APIs
        |
        +---- Policy RAG
        |
        +---- Conversation Memory
        |
        +---- Human Approval
        |
        +---- Ticket Escalation
        |
        v
Reliable Customer Support Workflow
```

The goal is to build an agentic customer-support system where the LLM handles natural-language understanding and workflow decisions while deterministic backend components enforce security, authorization, business rules, and state changes.
