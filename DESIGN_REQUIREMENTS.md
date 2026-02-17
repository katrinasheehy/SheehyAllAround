# 📋 Sheehy All-Around - Design Requirements (v2.2)

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
### **A. "Save & Scoop" Workflow (Historical/Standard)**
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
    * *Requirement:* Click specific event (e.g., "Beam") to see history graph for *just* that event.
    * *Metric:* Compare Personal Best (PB) vs. Seasonal Average.
2.  **Consistency Tracking:**
    * *Requirement:* Metric (Standard Deviation) showing "Stable" vs. "Volatile" events.
3.  **Judge Consistency (Context):**
    * *Requirement:* Calculate session average to contextualize performance.
    * *Metric:* **"Score vs. Field"** (e.g., "+0.400" vs. average).
4.  **Mobility Tracker (Future):**
    * *Requirement:* Progress bar towards qualifying score for next level.

---

## **5. Live Tracking Mode (Real-Time)**
* **Objective:** View scores and ranks update dynamically during a meet without manual refreshing.
* **Trigger:** "Live Mode" toggle in the app when today's date matches a scheduled meet.
* **Data Source (Technical Constraint):**
    * Since MSO blocks cloud scrapers, this requires a **Local Agent** (script running on user's laptop) to fetch data and push it to the app/database every 60 seconds.
* **Live Features:**
    1.  **Auto-Refresh:** Dashboard updates every 30-60 seconds.
    2.  **Dynamic Rank:** "Currently 3rd on Vault" (updates as other kids compete).
    3.  **"Flash" Updates:** Visual indicator (Green flash) when a new score is posted.
    4.  **Projected Finish:** "Needs a 9.4 on Floor to beat Personal Best AA."
    5.  **Session Context:** "Current Average on Beam is 8.8 (Judges are strict today)."

---

## **6. Technical Constraints**
* **Security:** Automated scraping is blocked by cloud protection (Cloudflare). Use manual HTML saves or Local Agent.
* **Hosting:** GitHub Codespaces (Development) -> Streamlit Cloud (Production).
* **Dependencies:** `pandas`, `beautifulsoup4`, `plotly`, `streamlit`.
