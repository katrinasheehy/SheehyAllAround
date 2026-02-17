# 📋 Sheehy All-Around - Design Requirements (v2.1)

## **1. Core Objective**
A unified, family-centric dashboard to track and visualize the gymnastics progress of the three Sheehy children (Annabelle, Azalea, Ansel). The app normalizes data from different organizations (Men's vs. Women's), handles historical imports, and provides context for scores.

---

## **2. User Profiles**
| Gymnast | Level | Theme Color | Events |
| :--- | :--- | :--- | :--- |
| **Annabelle** | Level 3 (Women's) | Pink (`#FF69B4`) | VT, UB, BB, FX |
| **Azalea** | Level 4 (Women's) | Purple (`#9370DB`) | VT, UB, BB, FX |
| **Ansel** | Level 4 (Men's) | Teal (`#008080`) | FX, PH, SR, VT, PB, HB |

---

## **3. Data Pipeline & Storage**
### **A. "Save & Scoop" Workflow (Current Standard)**
* **Input:** User saves athlete profile/meet result pages as `.html` files into the `ansel_history/` folder.
* **Processor:** `process_all_history.py` scans the folder, auto-detects the gymnast, and extracts data.
* **Storage:** Data is appended to `cleaned_gymnastics.csv`.

### **B. Data Schema (`cleaned_gymnastics.csv`)**
* **Core:** `Date`, `Gymnast`, `Meet`, `Session`, `Level`, `Division`
* **Performance:** `Meet_Rank` (e.g., "36"), `Meet_Rank_Total` (e.g., "152")
* **Scores:** Columns for all events (`VT`, `UB`, `BB`, `FX`, `PH`, `SR`, `PB`, `HB`) and `AA` (All-Around).
* **Context (PLANNED):** `Session_Average`, `Session_Median`, `Judge_Strictness_Index` (Score vs. Field Avg).

---

## **4. Feature Requirements**

### **A. Dashboard UI (Streamlit)**
1.  **Summary Header:**
    * Latest Meet Name & Date.
    * **Rank Badge:** "🏆 Rank: X / Y" (e.g., "5 / 42").
    * **Session Info:** Display "Level X • Division Y • Session Z".
2.  **Score Cards:**
    * Latest scores for that child's specific events.
    * Format: 3 decimals (`9.500`).
    * Handle missing data cleanly (`-`).
3.  **Trend Visualization:**
    * Line chart of **All-Around (AA)** scores over the season.

### **B. Advanced Analytics (In Progress)**
1.  **Event Drill-Down:**
    * *Requirement:* Ability to click a specific event (e.g., "Beam") and see a history graph for *just* that event, distinguishing between Personal Bests (PB) and average.
2.  **Consistency Tracking:**
    * *Requirement:* A metric (Standard Deviation) showing if a gymnast is "Stable" or "Volatile" on specific events.
3.  **Judge Consistency (Context):**
    * *Requirement:* Calculate the average score of *all* gymnasts in the session to contextualize performance.
    * *Metric:* **"Score vs. Field"** (e.g., "+0.400" means you beat the average, even if the score was low).
4.  **Mobility Tracker (Future):**
    * *Requirement:* Progress bar towards the qualifying score for the next level (e.g., "Need 36.00 AA for Level 5").

---

## **5. Technical Constraints**
* **Security:** Automated scraping is blocked by cloud protection (Cloudflare). Use manual HTML saves.
* **Hosting:** GitHub Codespaces (Development) -> Streamlit Cloud (Production).
* **Dependencies:** `pandas`, `beautifulsoup4`, `plotly`, `streamlit`.
