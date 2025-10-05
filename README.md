# Legal Case Predictor
Cieľom tohto projektu bolo vytvoriť program, ktorý dokáže analyzovať nový právny prípad a porovnať ho s databázou už zaznamenaných prípadov. Na základe podobnosti textu prográm vyhľadá najrelevantnejšie minulé prípady a následne využije OpenAI na návrh ďalších krokov a predikciu možného rozsudku.

Projekt tak spája základnú analýzu textu s umelou inteligenciou a predstavuje ukážku, ako by mohli fungovať systémy na podporu právnych rozhodnutí.

Vzhľadom na obmedzený prístup ku Codexis som použil simulovanú databázu právnych prípadov v textovom súbore `cases.txt`. Táto databáza obsahuje fiktívne prípady, ktoré umožnili demonštrovať funkcionalitu programu a overiť algoritmus vyhľadávania podobnosti a generovania promptu pre AI.

## Funkcionalita programu
1. **Príprava prostredia:**  
   - Uistite sa, že máte nainštalovaný Python (verzia 3.10 alebo vyššia).  
   - Nainštalujte knižnicu `openai` pomocou:
   - 
     ```bash
     pip install openai
     ```
2. **Nastavenie API kľúča:**  
   - Otvorte súbor `main.py`.  
   - Nastavte premennú `OPENAI_API_KEY` na váš OpenAI API kľúč:  
     ```python
     OPENAI_API_KEY = "YOUR_API_KEY_HERE"
     ```  
