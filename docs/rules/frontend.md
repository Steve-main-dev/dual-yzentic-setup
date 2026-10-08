# Frontend Architecture & UI Standards

This document establishes the architecture, state management, accessibility, and performance rules for frontend web development within `Yzentic-setup`.

---

## Overview

Modern web applications built with **React 19**, **Next.js**, and **Tailwind CSS** must be resilient, accessible, and fast by default. These standards mandate a server-first mental model, strict state separation, and aggressive bundle optimization to deliver world-class user experiences without layout shifts or bloated client bundles.

---

## Core Standards

### 1. Server-First Component Architecture (React 19 / RSC)
- **Default to React Server Components (RSC):** All components are Server Components by default unless client-side interactivity is required.
- **Push `"use client"` to Leaves:** Never mark entire layouts, templates, or page wrappers with `"use client"`. Confine client directives to small interactive leaf components (e.g., `<ThemeToggle />`, `<Combobox />`, `<AddToCartButton />`).
- **Data Fetching at the Tree Root:** Fetch data directly within Server Components; pass plain data down or use React 19 `use()` promise resolution.
- **Server Actions for Mutations:** Perform state-mutating operations through Server Actions or typed API endpoints with revalidation triggers (`revalidatePath`, `revalidateTag`).

### 2. State Management & Boundaries
- **Server Cache vs. Ephemeral UI State:**
  - **Server Cache:** Treat server data as a server-side cache. Do NOT duplicate server records into local `useState` or Redux/Zustand stores.
  - **Local UI State:** Use `useState` / `useReducer` solely for transient component state (e.g., modal open/close, accordion toggles).
  - **Global Client State:** Use lightweight stores (e.g., Zustand) only for cross-cutting client preferences (e.g., audio playback, multi-step unsaved client drafts).
- **Zero Prop Drilling:** For shared UI state spanning multiple component depths, utilize React Context or Zustand stores scoped to that feature subtree.

### 3. Canonical Component Reuse & Design System Registry
- **Mandatory Registry Check:** Before authoring ANY visual element (buttons, inputs, dialogs, dropdowns, cards, badges, sheets), you MUST inspect `@/components/ui/` (or the project's designated design system directory) first.
- **Zero Raw Primitives:** It is strictly forbidden to author custom `<button className="...">`, raw `<input>`, or ad-hoc modal overlays from scratch when a canonical component exists in `@/components/ui/`.
- **Canonical Component Manifest:**
  - Actions & Buttons: `@/components/ui/button`
  - Form Controls: `@/components/ui/input`, `@/components/ui/textarea`, `@/components/ui/select`, `@/components/ui/checkbox`, `@/components/ui/form`
  - Overlays & Popups: `@/components/ui/dialog`, `@/components/ui/sheet`, `@/components/ui/popover`, `@/components/ui/tooltip`
  - Feedback & Indicators: `@/components/ui/toast`, `@/components/ui/badge`, `@/components/ui/alert`
  - Layout & Grouping: `@/components/ui/card`, `@/components/ui/separator`, `@/components/ui/tabs`
- **Extending vs. Re-inventing:** If an existing component lacks a necessary variant or size, extend its variant definitions via `cva` inside the component file rather than creating an unvetted duplicate element.

### 4. Accessibility & Semantic Markup (WCAG 2.1 AA)
- **Semantic HTML First:** Use `<header>`, `<nav>`, `<main>`, `<article>`, `<aside>`, `<footer>`, and `<button>` elements. Never bind click handlers to generic `<div>` or `<span>` elements.
- **Keyboard Interactivity:** Every interactive element must be fully operable via keyboard (`Tab`, `Enter`, `Space`, `Escape`).
- **Focus Management:** Provide visible, high-contrast focus rings (`focus-visible:ring-2 focus-visible:outline-none`). Trap focus inside modal dialogs.
- **Accessible Primitives:** Leverage headless accessible primitives (Radix UI, shadcn/ui, Ariakit) rather than rolling custom unvetted dropdowns or modals.

### 5. Styling Conventions (Tailwind CSS)
- **Design Tokens over Arbitrary Values:** Use theme tokens (`text-primary`, `bg-muted`, `p-4`) instead of arbitrary one-off values (e.g., avoid `p-[17px]`, `text-[#1a2b3c]`).
- **Mobile-First Breakpoints:** Build the base layout for mobile screens first; add responsive overrides using `sm:`, `md:`, `lg:`, `xl:`.
- **Component Variants:** Use `cva` (class-variance-authority) and `cn()` (`clsx` + `tailwind-merge`) for clean, type-safe component variant management.

### 6. Performance Budgets & Core Web Vitals
- **Metric Targets:**
  - **Largest Contentful Paint (LCP):** < 2.5 seconds (preload hero fonts and hero images).
  - **Interaction to Next Paint (INP):** < 200 milliseconds (avoid blocking main-thread calculations).
  - **Cumulative Layout Shift (CLS):** < 0.1 (always provide explicit `width` and `height` on images and media containers).
- **Next.js Image Optimization:** Always use `next/image` with responsive `sizes` attribute. Never use raw `<img>` tags.
- **Bundle Budgeting:** Keep initial client JavaScript under 150KB gzip. Use dynamic imports (`next/dynamic` or `React.lazy`) for heavy dependencies (charts, rich text editors).

---

## Dos and Don'ts

| Do | Don't |
| :--- | :--- |
| **Do** import and compose canonical UI components from `@/components/ui/*`. | **Don't** author raw `<button>` or `<div>` elements with arbitrary Tailwind utility strings. |
| **Do** extend component variants using `cva` inside the design system folder. | **Don't** invent one-off dialogs, dropdowns, or forms that break visual consistency. |
| **Do** default to Server Components and fetch data on the server. | **Don't** slap `"use client"` at the top of a page file to make state work quickly. |
| **Do** use semantic HTML (`<button>`) with accessible keyboard handlers. | **Don't** add `onClick` to `<div>` without keyboard navigation or ARIA roles. |
| **Do** use `next/image` with explicit layout dimensions. | **Don't** use raw `<img>` tags that cause layout shifts (CLS regressions). |
| **Do** keep server data in the server cache and pass props down. | **Don't** copy server data into local `useState` and introduce synchronization bugs. |
| **Do** dynamically import heavy client modules (charts, rich editors). | **Don't** bundle massive third-party client libraries into the initial page payload. |
