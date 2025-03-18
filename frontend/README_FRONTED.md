---

# **📂 Project Structure Guide**

This document explains the purpose of each folder and file in the project to help new developers quickly understand the codebase.

---

## **🗂️ Folder Structure Overview**

```
frontend/
│── src/
│   ├── assets/
│   ├── auth/
│   ├── components/
│   │   ├── ui/
│   ├── hooks/
│   ├── Layout/
│   ├── lib/
│   ├── pages/
```

---

## **📁 1. assets/**
- Stores **static files** like images, icons, fonts, or other assets used in the UI.

---

## **📁 2. auth/** _(Authentication Logic)_
Manages user authentication and authorization.

- **`AuthContext.tsx`** – Provides authentication state using the **Context API**.
- **`hooks.tsx`** – Contains custom hooks like `useAuth(), useUser()` for authentication logic.
- **`index.tsx`** – Re-exports authentication-related modules.
- **`routing.tsx`** – Handles protected routes (e.g., restricting access to logged-in users).

---

## **📁 3. components/** _(Reusable UI Components) Shadcn_
Contains reusable components for the frontend.

### **📂 ui/** _(User Interface Components)_
- **`app-sidebar.tsx`** – Defines the sidebar navigation.
- **`loginForm.tsx`** – Login form with email/password input fields.
- **`mode-toggle.tsx`** – Switch for Dark Mode / Light Mode.
- **`nav-main.tsx`** –   Manages the **main navigation bar**.  
- **`nav-projects.tsx`** – Displays project-based navigation.
- **`nav-user.tsx`** – Handles user profile navigation.
- **`registerForm.tsx`** – User registration form.
- **`team-switcher.tsx`** – Allows users to switch between teams.
- **`theme-provider.tsx`** – Manages global theme settings.

---

## **📁 4. hooks/** _(Custom React Hooks)_
Contains reusable **logic-based functions** Used by chat page.

- Examples:
  - `useAuth()` – Handles authentication logic.
  - `use-audio-recording()`
  - `useTheme()` – Manages Dark Mode toggle.
  - `useFetch()` – Custom hook for fetching API data.

---

## **📁 5. Layout/** _(Page Layout Components)_
Defines reusable layout components such as headers, footers, and dashboards.

- Example components:
  - Uses various components from the `ui/` folder to create a complete layout.

---

## **📁 6. lib/** _(Utility Functions & Helper Files)_
Stores helper functions used across the application.

- **`allAuth.tsx`** – Helper functions for authentication. All API functions are mentioned here for auth.
- **`audio-utils.ts`** – Functions for **audio processing** (e.g., voice commands, playing sound).
- **`cerfToken.ts`** – Handles **security logic**, like CSRF tokens.
- **`utils.ts`** – General **utility functions** (e.g., date formatting, API requests).

---

## **📁 7. pages/** _(Main Application Pages)_
Contains **top-level pages** for the application.

  - `Home.tsx` – Homepage.
  - `Chat.tsx` – Chat page.
  

---



```markdown
# **📂 Project Structure Guide**

This document explains the purpose of each folder and file in the project to help new developers quickly understand the codebase.

---

## **🗂️ Folder Structure Overview**

```markdown
frontend/
│── src/
│   ├── assets/
│   │   └── README.md
│   ├── auth/
│   │   ├── AuthContext.tsx
│   │   ├── hooks.tsx
│   │   ├── index.tsx
│   │   └── routing.tsx
│   ├── components/
│   │   ├── ui/
│   │   │   ├── app-sidebar.tsx
│   │   │   ├── loginForm.tsx
│   │   │   ├── mode-toggle.tsx
│   │   │   ├── nav-main.tsx
│   │   │   ├── nav-projects.tsx
│   │   │   ├── nav-user.tsx
│   │   │   ├── registerForm.tsx
│   │   │   ├── team-switcher.tsx
│   │   │   └── theme-provider.tsx
│   │   └── README.md
│   ├── hooks/
│   │   ├── useAuth.tsx
│   │   ├── useTheme.tsx
│   │   ├── useFetch.tsx
│   │   └── README.md
│   ├── Layout/
│   │   ├── DashboardLayout.tsx
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── README.md
│   ├── lib/
│   │   ├── allAuth.tsx
│   │   ├── audio-utils.ts
│   │   ├── cerfToken.ts
│   │   ├── utils.ts
│   │   └── README.md
│   └── pages/
│       ├── Home.tsx
│       ├── Chat.tsx
│       └── README.md
```

---

## **📁 1. assets/**
- Stores **static files** like images, icons, fonts, or other assets used in the UI.

---

## **📁 2. auth/** _(Authentication Logic)_
Manages user authentication and authorization.

- **`AuthContext.tsx`** – Provides authentication state using the **Context API**.
- **`hooks.tsx`** – Contains custom hooks like `useAuth()` for authentication logic.
- **`index.tsx`** – Re-exports authentication-related modules.
- **`routing.tsx`** – Handles protected routes (e.g., restricting access to logged-in users).

---

## **📁 3. components/** _(Reusable UI Components)_
Contains reusable components for the frontend.

### **📂 ui/** _(User Interface Components)_
- **`app-sidebar.tsx`** – Defines the sidebar navigation.
- **`loginForm.tsx`** – Login form with email/password input fields.
- **`mode-toggle.tsx`** – Switch for Dark Mode / Light Mode.
- **`nav-main.tsx`** –   Manages the **main navigation bar**.  
- **`nav-projects.tsx`** – Displays project-based navigation.
- **`nav-user.tsx`** – Handles user profile navigation.
- **`registerForm.tsx`** – User registration form.
- **`team-switcher.tsx`** – Allows users to switch between teams.
- **`theme-provider.tsx`** – Manages global theme settings.

---

## **📁 4. hooks/** _(Custom React Hooks)_
Contains reusable **logic-based functions**.

- Examples:
  - `useAuth()` – Handles authentication logic.
  - `useTheme()` – Manages Dark Mode toggle.
  - `useFetch()` – Custom hook for fetching API data.

---

## **📁 5. Layout/** _(Page Layout Components)_
Defines reusable layout components such as headers, footers, and dashboards.

- Example components:
  - `DashboardLayout.tsx` – Main layout for the user dashboard.
  - `Header.tsx` – Defines the app header.
  - `Footer.tsx` – Defines the footer.

---

## **📁 6. lib/** _(Utility Functions & Helper Files)_
Stores helper functions used across the application.

- **`allAuth.tsx`** – Helper functions for authentication (e.g., handling JWT tokens).
- **`audio-utils.ts`** – Functions for **audio processing** (e.g., voice commands, playing sound).
- **`cerfToken.ts`** – Handles **security logic**, like CSRF tokens.
- **`utils.ts`** – General **utility functions** (e.g., date formatting, API requests).

---

## **📁 7. pages/** _(Main Application Pages)_
Contains **top-level pages** for the application.

  - `Home.tsx` – Homepage.
  - `Chat.tsx` – Chat page.
```