# Design Specification: Kanban Project (Cobalt Kinetic)

## 1. Design Vision & Principles
The goal of this design was to create a "slick, professional, and gorgeous" MVP for a Kanban-style project management application. The focus is on high utility and minimal cognitive load.

*   **Clean & Focused:** Minimalist aesthetic that prioritizes the task cards and column organization.
*   **Tactile Feedback:** Subtle shadows and transitions to make the digital board feel responsive and "physical."
*   **Professional Palette:** A high-contrast combination of Dark Navy and bright Primary Blue, accented with functional Purple and Yellow.

---

## 2. Visual Foundation

### Color Palette
| Usage | Color Name | Hex Code |
| :--- | :--- | :--- |
| **Primary** | Cobalt Blue | `#209dd7` |
| **Secondary** | Royal Purple | `#753991` |
| **Background (Nav/Headers)** | Dark Navy | `#032147` |
| **Accent** | Kinetic Yellow | `#ecad0a` |
| **Typography (Secondary)** | Gray Text | `#888888` |
| **Card Background** | Paper White | `#ffffff` |
| **Surface Background** | Ghost White | `#f8fafc` |

### Typography
*   **Primary Font:** Manrope (Clean, modern, highly readable sans-serif)
*   **Scale:**
    *   *Headings:* Bold, tracking-tight, `#032147`
    *   *Body:* Medium weight, standard tracking, `#032147` or `#888888`

---

## 3. UI Components & Elements

### The Kanban Card
*   **Structure:** Simple white surface with `shadow-sm`.
*   **Title:** Bold Navy text.
*   **Details:** Small Gray supporting text.
*   **Interactions:** 
    *   Hover state reveals Edit (Rename) and Delete (Trash) icons.
    *   Transition: 300ms ease-in-out for icon visibility.

### Kanban Columns
*   **Fixed Layout:** 5 columns per board.
*   **Header:** Inline editing for renaming column titles.
*   **Add Action:** Dotted-border "Add Card" button at the bottom of each column for quick entry.

### Navigation (The "Cognitive Atelier" Shell)
*   **Side Bar:** Persistent Dark Navy rail for high-level navigation.
*   **Top Bar:** Translucent white backdrop with blur effect to maintain context while scrolling.

---

## 4. User Interactions & States
*   **Rename Card:** Triggers an inline text field to replace the title.
*   **Delete Card:** Instant removal with a subtle fade-out transition.
*   **Empty States:** Clear "Add Card" placeholders to guide user behavior.
