# LRP_metaheuristics

Zwei Metaheuristiken basierend auf Marinakis (2015) und Quintero-Araujo et al. (2021) für das kapazitätsbeschränkte location routing problem mit stochastischem Bedarf (CLRPSD), umgesetzt in Python, ausgelegt zur Verwendung als Docker Container. 

Entwickelt im Zuge der Masterarbeit "Metaheuristiken für das Location Routing Problem  mit stochastischen Bedarfen – Umsetzung mit MiniZinc und Python" von Jakob Baumann, Universität Augsburg.

Anmerkung: Diese Repository ist derzeit nicht auf höchste Benutzerfreundlichkeit ausgelegt. Die folgenden Beschreibungen und Anleitungen sollen aber helfen, zumindest ein wenig zu experimentieren.

## Inhalt

Dieses Repository enthält zwei, zur Verwendung als Docker Container/Image ausgelegte Komponenten, `minizinc` und `metaheuristik`.

Die `minizinc` Komponente enthält ein Python Steuermodul, eine MiniZinc Datei und einige Instanzen. Mit dem Python Steuermodul kann das in der MiniZinc Datei beschriebene CLRPSD Modell eine der gewählten Instanzen lösen. 

Die `metaheurisik` Komponente enthält zwei Metaheuristiken, mehrere Instanzen, einen Figure-Ordner, und ein Python Modul. Mit dem Python Steuermodul werden die Instanz, einige Parameter und die Metaheuristik gewählt. Die Ergebnisse/die Lösung der Metaheuristk werden im Figure-Ordner als SVG Datei gespeichert. 


## Bedienung

Zunächst prüfen, ob Docker auf dem Betriebssystem installiert ist und läuft. Die Python Skripte [metaheuristik/metaheuristicSolver.py](metaheuristik/metaheuristicSolver.py) und [minizinc/py/M+QA_MiniZinc2Python.py](minizinc/py/M+QA_MiniZinc2Python.py) lassen sich zwar auch direkt ausführen, allerdings müssen dann sehr wahrscheinlich händisch einige Pfade angepasst und Bibliotheken importiert werden. Hier ein [Tutorial zur Installation von Docker auf Windows](https://docs.docker.com/desktop/install/windows-install/).

### Metaheuristik

1. Die Batch [metaheuristik/CreateImageAndContainer.cmd](metaheuristik/CreateImageAndContainer.cmd) ausführen. Das ist nur beim ersten Start erforderlich, danach geht auch [metaheuristik/ExecuteContainer.cmd](metaheuristik/ExecuteContainer.cmd). Die Batch macht folgendes:
   - Führt die Dockerfile aus
   - Mappt die benötigten Ordner
   - Erstellt das Image
   - Startet den Container
2. In der Kommandozeile erscheinen Auswahloptionen:
   1. `Choose from` Auswahl der Instanz: Eine Liste der verfügbaren [Instanzen](metaheuristik/instances/) wird angezeigt. Zur Auswahl die dazugehörige (Nummer) eingeben.
   2. `Number of times metaheuristic is executed` Anzahl an parallelen Ausführungen der Metaheuristik. Jede Ausführung läuft auf einem eigenen Prozess und erzeugt eine eigenen Lösung. Es werden höchstens 6 Ausführungen parallel durchgeführt. Diese Anzahl kann in [metaheuristik/metaheuristicSolver.py](metaheuristik/metaheuristicSolver.py) angepasst weren. Standard ist 1.
   3. `Number of iterations per metaheuristic-execution` Anzahl an Durchführungen der einzelnen Metaheuristik. Konkreter, gibt an wie oft die Hauptphase der danach gewählten Metaheuristik ausgeführt wird. Standard ist 100, beachte allerdings, dass höhere Zahlen zu längeren Laufzeiten und umgekehrt führen. 
   4. `GLCENTPSO by Marinakis (1) or SimILS by Quintero-Araujo et al. (2)` Wähle eine Metaheurisitk aus, entsprechend 1 oder 2 eingeben.
   5. Falls Quintero-Araujo et al. (2) gewählt wurde: `Enter maximum Safety Stock:` Eingabe des Maximalen Sicherheitsbestandes in %. Bei nicht-stochastischen Problemen kann hier 0 eingegeben werden, bei stochastischen bis zu 10.
3. Warten
4. Das Ergebnis wird ausgegeben und als SVG im Ordner [Figures](metaheuristik/figures/) gespeichert. Der Dateiname gibt dabei an: Metaheuristik, Instanz, Varianzfaktor, Gesamtkosten (TC), Routenkosten(RC), Laufzeit des Programms (TSec) und ob es der Routenplan mit (Strategy) oder ohne Strategie ist. 

### MiniZinc

1. Die Batch [minizinc/CreateImageAndContainer.cmd](minizinc/CreateImageAndContainer.cmd) ausführen. Das ist nur beim ersten Start erforderlich, danach geht auch [minizinc/ExecuteContainer.cmd](minizinc/ExecuteContainer.cmd). Die Batch macht folgendes:
   - Führt die Dockerfile aus
   - Mappt die benötigten Ordner
   - Erstellt das Image
   - Startet den Container
2. Führt automatisch die Datei [minizinc/py/M+QA_MiniZinc2Python.py](minizinc/py/M+QA_MiniZinc2Python.py) aus. Löst standardmäßig eine 3 Kunden 2 Fahrzeuge 2 Standorte Instanz. Ist leider noch hardgecoded. Für eine andere Instanz aus dem Ordner [minizinc/dzn/](minizinc/dzn/) in der .py die Zeile 64 ändern: `dznFileName = "/CLRPSD_M+QA_3K_2V_1F_4docker.dzn"`
3. Ggf. Warten. ACHTUNG: Dieses Modell wird exakt gelöst, dauert entsprechend bei großen Instanzen (ab 5 Kunden) sehr lange (>60 Minuten). Lediglich die voreingstellte Instanz ist innerhalb kurzer Zeit lösbar. 
4. Das Ergebnis wird nur auf Kommandozeile ausgegeben, es wird hier keine grafische Lösungsdarstellung erzeugt.

## Instanzen

Informationen zur Erstellung von Instanzen verwendet von den Metaheuristiken. Am einfachsten eine bestehende Instanz kopieren und nach Bedarf abändern.

Bestandteile:
- `coord`: Liste von Koordinaten der Kunden und (anschließend!) Standorte. Wichtig: Platzhalter `[0,0]` muss an erster Stelle stehen!
- `demandList`: Liste der Bedarfe der Kunden. Selbe Reihenfolge wie bei `coord`. Bedarf als Dictionary wie folgt: `{Bedarf:Eintrittswahrscheinlichkeit}`. Wenn eine deterministische Instanz oder eine stochastische Instanz mit Poisson Verteilung (marinakis) oder Log-normal (quintero-araujo) erstellt werden soll, dann lediglich {Erwartungswert:1}. Sollen stattdessen bestimmte diskrete Bedarfe verwendet werden, dann {Bedarf1:Wkeit1, Bedarf2:Wkeit2,...}, bei Bedarf individuell für jeden Kunden.
- `customers`: Liste der Kunden-IDs, aufsteigend, startend bei 1. 
- `totalVehicleCap`: Ladungskapazität der/des Fahrzeuge/s.
- `numParticles`: Anzahl der Partikel bei Marinakis/GLCENTPSO
- `facilities`: Liste der Standort-IDs, aufsteigend, beginnend mit der letzten Kundennummer+1
- `fOpeningCosts`: Liste Standortkosten der jeweiligen Standorte
- `fCapacity`: Liste der Kapazität der jeweiligen Standorte
- `variance`: Optional. Gibt den Varianzfaktor für die stochastischen Bedarfe bei Quintero-Araujo an. Getestete Werte sind 0.0, 0.05,0.1,0.15.
- `poisson`: Optional. Gibt an, dass bei Marinakis stochastische, Poisson-Verteilte Bedarfe verwendet werden sollen. True/False.

WICHTIG: Deterministische Instanzen können von beiden Metaheursitiken verwendet werden. Stochastische Instanzen sollten unterteilt werden: Entweder `variance` mit quintero-araujo/SimILS21 verwenden oder `poisson` mit marinakis/GLCENTPSO verwenden. Ansonsten kann es in der aktuellen Version zu Laufzeitproblemen kommen. 





