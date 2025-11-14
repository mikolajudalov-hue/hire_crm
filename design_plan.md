# Design Plan: Transformation to an Advanced System UI

The user has requested a redesign of the existing application to make it look like a "sophisticated, feature-rich system" with numerous informational blocks. The current design is a clean, light-themed corporate style. To meet the user's request, the redesign will focus on a **Dark Mode** aesthetic and a **dense, widget-based dashboard layout** to convey complexity and advanced functionality.

## 1. Aesthetic Transformation: Dark Mode

A dark theme is a common visual language for "advanced" or "technical" systems (e.g., monitoring dashboards, IDEs). This will be the foundation of the new design.

| Element | Current Style (Light) | New Style (Dark) | CSS Variable/Value |
| :--- | :--- | :--- | :--- |
| **Primary Background** | `#F5F5F7` (Light Gray) | `#121212` (Deep Black/Gray) | `--bg-primary` |
| **Secondary Background** | `#FFFFFF` (White) | `#1E1E1E` (Dark Card) | `--bg-secondary` |
| **Text Color** | `#1D1D1F` (Dark Gray) | `#E0E0E0` (Light Gray) | `--text-primary` |
| **Muted Text Color** | `#86868B` (Muted Gray) | `#A0A0A0` (Muted Light Gray) | `--text-muted` |
| **Primary Accent Color** | `#007AFF` (Apple Blue) | `#00C8FF` (Electric Blue/Cyan) | `--color-primary` |
| **Card Shadow** | Subtle, light shadow | Subtle, dark shadow (e.g., `0 4px 12px rgba(0, 0, 0, 0.5)`) | |
| **Border/Divider** | `#D2D2D7` (Light Border) | `#333333` (Dark Border) | `--border-color` |

## 2. Layout and Structure

The main layout will be converted into a grid-based dashboard to support a high density of information.

*   **Dashboard Grid:** The main content area (`dashboard.html`) will use a CSS Grid layout, allowing for multiple columns and flexible arrangement of informational blocks.
*   **Sidebar/Navigation:** A simple, dark-themed left-hand navigation will be introduced in `base.html` to simulate a complex system with multiple modules, even if only the existing links are used.

## 3. Informational Blocks (Widgets)

The core of the "sophisticated system" look will be achieved by replacing the simple "Quick Stats" section with a variety of new, visually distinct widgets. These widgets will use the existing data (`name`, `pesel`, `months`) and new placeholder data to simulate a rich data environment.

### New Widget Types to be Implemented:

1.  **System Status Panel (Top-Level):**
    *   **Content:** User Name, PESEL (as a "User ID"), System Status (Online/Offline), Last Data Sync Time (placeholder).
    *   **Aesthetic:** Prominent, with a clear status indicator light (green/red dot).

2.  **Data Overview Cards (Small, 3-4 columns):**
    *   **Content:** Total Months Available, System Version, Access Level (e.g., "Level 5 - Admin"), and a new metric like "Security Score" (placeholder).
    *   **Aesthetic:** Small, high-contrast cards with large numbers and small labels.

3.  **Activity/Log Feed (List-based):**
    *   **Content:** A simulated log of recent system activities (e.g., "Login successful," "Data request initiated," "Report generated").
    *   **Aesthetic:** Monospace font, time-stamped entries, and color-coded status (e.g., `[INFO]`, `[WARN]`, `[CRIT]`).

4.  **Data Visualization Placeholder (Chart Area):**
    *   **Content:** A large, empty area with a title like "Real-time Data Stream Analysis" or "Historical Trend Projection."
    *   **Aesthetic:** Dark background, light grid lines, and a placeholder for a line/bar chart to suggest complex data processing.

5.  **Action/Control Panel (Form Refinement):**
    *   **Content:** The existing month/type selection form, but styled to look like a control panel with clear, distinct buttons and inputs.

## 4. Implementation Strategy

1.  **Update `style.css`:** Introduce CSS variables for the dark theme and implement the new styles for the body, cards, and text. Add new utility classes for the grid layout and log feed.
2.  **Update `base.html`:** Implement the new dark theme body class and introduce a minimal sidebar structure.
3.  **Update `dashboard.html`:** Completely restructure the content using the new grid layout and populate it with the new informational blocks/widgets defined above, using Jinja2 variables where possible and placeholder data otherwise.
4.  **Update `hours.html` and `salary.html`:** Apply the new dark theme and potentially wrap the tables in a new "Data Report" widget style to maintain consistency.

This plan ensures a complete visual overhaul that transforms the simple application into a convincing "advanced system" dashboard.
