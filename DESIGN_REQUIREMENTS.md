# 📋 Sheehy All-Around - Design Requirements (v2.3)

## **1. Core Objective**
A unified, family-centric dashboard to track and visualize gymnastics progress for Annabelle, Azalea, and Ansel. Normalizes data across Men's/Women's disciplines and provides context for scores.

---

## **2. User Profiles**
| Gymnast | Level | Theme Color | Events |
| :--- | :--- | :--- | :--- |
| **Annabelle** | Level 3 (W) | Pink (`#FF69B4`) | VT, UB, BB, FX |
| **Azalea** | Level 4 (W) | Purple (`#9370DB`) | VT, UB, BB, FX |
| **Ansel** | Level 4 (M) | Teal (`#008080`) | FX, PH, SR, VT, PB, HB |

---

## **3. Data Pipeline & Storage**
### **A. "Save & Scoop" Workflow**
* **Input:** Manual HTML saves from MSO to `ansel_history/`.
* **Processor:** `process_all_history.py` parses metadata and scores.

### **B. Data Schema (`cleaned_gymnastics.csv`)**
* **Core:** `Date`, `Gymnast`, `Meet`, `Session`, `Level`, `Division`.
* **Overall Performance:** `Meet_Rank`, `Meet_Rank_Total`.
* **Event Scores & Ranks:** * Scores: `VT`, `UB`, `BB`, `FX`, `PH`, `SR`, `PB`, `HB`, `AA`.
    * **Ranks:** Each event must have a corresponding rank column (e.g., `VT_Rank`, `UB_Rank`, `AA_Rank`).
* **Context (PLANNED):** `Session_Average`, `Session_Median`.

 ### **C. Session Context Pipeline (NEW)**
* **Objective:** Collect EVERY athlete's score for sessions attended by the Sheehy kids in 2026.
* **Input:** Automatically derived from `cleaned_gymnastics.csv` (2026 rows).
* **Storage:** `session_raw_data.csv` (Full session table).
* **Validation:** Script must confirm "Athletes Found" matches "Meet_Rank_Total" from the primary CSV.
---

## **4. Feature Requirements**
### **A. Dashboard UI**
1. **Summary Header:** Rank Badge ("🏆 Rank: X / Y") and Session Info.
2. **Score Cards:** 3-decimal display for specific gymnast events.
3. **Trend Visualization:** Line chart of All-Around (AA) scores.

### **B. Advanced Analytics**
1. **Event Drill-Down:** View history/trend for a single event (e.g., "Just Beam").
2. **Consistency Tracking:** Standard Deviation per event (Stable vs. Volatile).
3. **Judge Consistency:** Compare score vs. Session Average (+/- Diff).

---

## **5. Live Tracking Mode (Real-Time)**
* **Objective:** Dynamic updates during a meet via a **Local Agent** script.
* **Live Features:** Auto-refresh, Dynamic Rank, Projected Finish (e.g., "Needs 9.2 on Floor for PB").

---

## **6. Technical Constraints**
* **Cloud Blocking:** MSO blocks Cloudflare. Requires local HTML saves or local agent.
* **Deduplication:** Must keep "last" entry to allow data enrichment of existing meets.

---

## **7. Active Bug & Data Debt Tracker**
* [ ] **Data Cleanup - Ansel:** Recent imports missing Division/Session metadata.
* [ ] **Data Cleanup - Mardi Gras Meet:** Girls' data missing ranks and session info.
* [ ] **Missing Ranks:** Populate `[Event]_Rank` columns for all historical data.
* [ ] **Blank Cells:** Ensure `fillna("")` is handled in the processor to prevent app crashes.
