# Hotello WhatsApp AI Chatbot – Technical Architecture

## 1. Overview

The **Hotello WhatsApp AI Chatbot** is a production-grade, microservice-based conversational system that enables users to search hotels, manage bookings, and get assistance via WhatsApp. It integrates Meta’s WhatsApp Cloud API, a Python-based AI middleware powered by **Gemini**, and the existing **Hotello MERN backend**.

The architecture prioritizes:

* Service separation
* Scalability
* Security
* Vendor flexibility (AI/provider agnostic)
* Reuse of existing Hotello business logic

---

## 2. High-Level Architecture

```
User (WhatsApp)
   ↓
Meta WhatsApp Cloud API
   ↓ (Webhook Events)
WhatsApp Bot Service (Python / Flask)
   ↓ (Secure REST calls)
Hotello Backend API (Node.js / Express)
   ↓
MongoDB
```

---

## 3. Core Design Principles

* **Microservice Separation**: WhatsApp bot runs as an independent service
* **Backend as Source of Truth**: All business logic remains in Hotello backend
* **Stateless AI Layer**: No persistent state stored in the bot service
* **Security First**: Webhook verification, signed payloads, API authentication
* **Scalability**: Horizontally scalable services

---

## 4. System Components

### 4.1 WhatsApp Client

* End users interact via WhatsApp (mobile or web)
* Supports text-based conversational input
* Entry point for hotel discovery and booking flows

---

### 4.2 Meta WhatsApp Cloud API

**Responsibilities**:

* Message delivery
* Webhook event dispatch
* Business verification
* Template enforcement (24-hour rule)

**Key Capabilities**:

* Inbound message events
* Outbound text and template messages
* Webhook signature validation

---

### 4.3 WhatsApp Bot Service (Python / Flask)

This service acts as the **AI orchestration and messaging gateway**.

#### Responsibilities

* Receive and validate WhatsApp webhook events
* Normalize incoming messages
* Generate AI-driven responses
* Route user intents to Hotello backend APIs
* Send responses back to WhatsApp

#### Tech Stack

* Python 3.10+
* Flask
* google-generativeai (Gemini)
* Requests / HTTPX

#### Internal Modules

```
app/
├── run.py                  # Flask app entry
├── webhook.py              # Webhook routes
├── security.py             # Signature + token validation
├── whatsapp_utils.py       # Message parsing & sending
├── gemini_service.py       # AI response generation
├── intent_router.py        # Intent detection & mapping
└── config.py               # Environment configuration
```

---

### 4.4 Gemini AI Layer

**Role**: Natural language understanding and response generation

#### Usage Patterns

* Intent classification
* Conversational replies
* Parameter extraction (location, dates, budget)

#### Model

* `gemini-1.5-flash`

#### Prompt Strategy

* System-prompted as “Hotello Concierge”
* Guardrails to restrict unsupported actions

---

### 4.5 Hotello Backend API (Node.js)

The backend remains **unchanged** and acts as the authoritative business service.

#### Responsibilities

* Hotel search & filtering
* Booking creation & management
* User profile & booking retrieval
* Authentication & authorization

#### AI-Specific Endpoints (Recommended)

```
POST /api/ai/search-hotels
POST /api/ai/create-booking
GET  /api/ai/my-bookings
POST /api/ai/cancel-booking
```

---

### 4.6 Database (MongoDB)

* Stores hotels, bookings, users
* Accessed only by Hotello backend
* No direct database access from bot service

---

## 5. Data Flow Scenarios

### 5.1 Hotel Search

1. User sends: “Find hotels in Ella under 20k”
2. WhatsApp Cloud API sends webhook event
3. Bot validates payload signature
4. Gemini extracts intent and parameters
5. Bot calls `POST /api/ai/search-hotels`
6. Backend returns hotel list
7. Bot formats response
8. Message sent back to WhatsApp

---

### 5.2 Booking Creation

1. User confirms booking details
2. Bot validates conversational state
3. Bot sends booking payload to backend
4. Backend persists booking
5. Confirmation message sent to user

---

## 6. Security Architecture

### 6.1 Webhook Verification

* `hub.verify_token` validation on setup
* SHA256 payload signature validation
* Reject unsigned or tampered payloads

### 6.2 Service-to-Service Authentication

Recommended options:

* Static API key header
* Short-lived JWT issued by backend

Example:

```
Authorization: Bearer <BOT_API_TOKEN>
```

### 6.3 Secrets Management

* Environment variables only
* No secrets committed to source control

---

## 7. Deployment Architecture

### 7.1 Services

| Service      | Platform         |
| ------------ | ---------------- |
| Frontend     | Vercel           |
| Backend API  | Render           |
| WhatsApp Bot | Render / Railway |

### 7.2 Networking

* Public HTTPS webhook endpoint
* Internal REST calls over HTTPS
* No inbound DB exposure

---

## 8. Scalability & Reliability

* Stateless bot service enables horizontal scaling
* Backend rate-limits AI-triggered endpoints
* Graceful degradation when AI is unavailable

---

## 9. Observability

* Structured logging (JSON)
* Error tracking via platform logs
* Request correlation IDs

---

## 10. Future Enhancements

* Multi-language support (Sinhala / Tamil)
* Payment initiation via WhatsApp
* Vector search for semantic hotel matching
* Admin-controlled AI responses
* WhatsApp rich message templates

---

## 11. Repository Strategy

* `hotello/` – frontend & backend
* `hotello-whatsapp-bot/` – Python bot microservice

Clear ownership, independent CI/CD, and clean boundaries.

---

## 12. Summary

This architecture delivers a **secure, scalable, AI-powered WhatsApp concierge** that integrates seamlessly with Hotello’s existing platform while remaining flexible for future growth and AI evolution.

The system is production-ready, vendor-agnostic, and aligned with modern cloud-native best practices.
