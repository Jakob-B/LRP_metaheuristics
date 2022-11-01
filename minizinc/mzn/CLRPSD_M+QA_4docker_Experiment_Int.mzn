% CLRPSD mit DP/rekursivem Tourkostenberechnung von Marinakis und CLRP von Quintero-Araujo et al.


%Parameter

%%Vehicles
int: num_vehicles;
set of int: vehicles;
int: transportCapacity;
array[vehicles] of int: utilityCost;

%% Knoten (Standorte und Kunden)
int: num_nodes;
set of 1..num_nodes: nodes;

%% Kunden
int: num_customers;
set of int: customers;
%array[0..num_customers,0..num_customers] of int: travelCost;
array[customers, 0..transportCapacity] of 0..1: demandProb; %Bedarf ist stochastische Variable

%% Kunden Subsets
int: numSubsets;
array[1..numSubsets] of var set of customers: customersInSubset;

%% Standorte
int: num_facilities;
set of int: facilities;
array[facilities] of int: storageCapacity;
array[facilities] of int: fixcost;

%% Kanten
array[nodes,nodes] of int: travelCost;


%Entscheidungsvariablen

%% Fahrt
array[nodes,nodes,vehicles] of var 0..1: f; 


%%Standorteröffnung
array[facilities] of var 0..1: y; %open
%%Fahrzeug wird auf Route von Depot aus eingesetzt
array[facilities,vehicles] of var 0..1: z; %depotDepart: Fahrzeug startet bei Depot
%% Kundenzuweisung zu Depot
array[customers, facilities] of var 0..1: x;
%%Fahrkosten Apriori Route
%&Routenkosten nach Bedienung von Kunde mit Restkapazizät
%array[nodes,nodes,vehicles,0..transportCapacity] of var 0.00..200.00: routingCost;
%array[nodes,nodes,vehicles,0..transportCapacity] of var 0.00..200.00: fProceed;
%array[nodes,nodes,vehicles,0..transportCapacity] of var 0.00..200.00: fReturn;
%array[nodes,nodes,vehicles,0..transportCapacity] of var 0..1: s;

%array[nodes,vehicles,0..transportCapacity] of var 0.00..200.00: routingCost1;
%array[nodes,vehicles,0..transportCapacity] of var 0.00..200.00: fProceed1;
%array[nodes,vehicles,0..transportCapacity] of var 0.00..200.00: fReturn1;
array[nodes,vehicles,0..transportCapacity] of var 0..1: s1;



int: BigM = 10000000;

var 0..100000: ZF;

%% Test: Dvar auf eine Nachkommastelle runden
array[nodes,vehicles,0..transportCapacity] of var 0..200000: routingCostInt1;
array[nodes,vehicles,0..transportCapacity] of var 0..200000: fProceedInt1;
array[nodes,vehicles,0..transportCapacity] of var 0..200000: fReturnInt1;

%Zielfunktion

solve minimize ZF; 

% Nebenbedingungen

%% ZF (3.1.1)
constraint ZF >= sum(w in facilities)(fixcost[w]*y[w])
  + sum(k in vehicles, w in facilities, i in customers) (utilityCost[k] * f[w,i,k])
  + sum(w in facilities, k in vehicles) (routingCostInt1[w,k,transportCapacity]/100)
;

%% QA_NB_KundeMussBedientWerden(3.1.3):
constraint forall(i in customers)(sum(k in vehicles, n in nodes where n!=i)(f[n,i,k]) == 1);

%% QA_NB_Flusserhaltung(3.1.5):
constraint forall(k in vehicles, n in nodes)(
    sum(m in nodes)(f[n,m,k]) == sum(m in nodes)(f[m,n,k])
  ); 
  
%% QA_NB_NurEinBesuch_Prins(3.1.6):
constraint forall(k in vehicles)(
    sum(w in facilities, n in nodes)(f[w,n,k])<= 1
);

%% QA_NB_SubTourElimination(3.1.7):
constraint forall(k in vehicles, a in 1..numSubsets)(
    sum(n in customersInSubset[a], m in customersInSubset[a])(f[n,m,k])<= sum(ss in customersInSubset[a])(1)-1
  ); 

%% QA_NB_BedienungNurVonOffenenStandorten(3.1.8):
constraint forall(i in customers, w in facilities, k in vehicles)(
    sum(j in customers)(f[w,j,k])+sum(n in nodes)(f[n,i,k])<=1+x[i,w]
  );

%% M_NB_StandortKapazitaet(3.2.2) statt (3.1.9):
constraint forall(w in facilities)(
    sum(k in vehicles)(transportCapacity*z[w,k])<=storageCapacity[w]*y[w]
  );

%% M_NB_StartNurWennOffen(zusätzliche (neue) NB (3.3.2); folgt aus 3.2.2?):
%% wird benötigt, weil z benötigt wird für DP. 
constraint forall(k in vehicles, w in facilities)(
    sum(i in nodes)(f[w,i,k])<= z[w,k]
  );
  
%% M_NB_FahrzeugNurEinStartDepot(?nein, ist doch dasselbe wie 3.1.6?):
%constraint forall(k in vehicles)(
%    sum(i in customers,w in facilities)(f[w,i,k])<= 1
%  );
  
%% M_NB_Grenzbedingung (3.3.6):
%% Kosten zurück ins Depot immer Fahrtkosten zum Depot, egal welche verbleibende Kapazität.
%% Dieser Fall tritt ein, wenn der letzte Kunde bedient wurde.
constraint forall(q in 0..transportCapacity, i in customers, k in vehicles, w in facilities)(
    routingCostInt1[i,k,q] >= travelCost[i,w]*f[i,w,k]*100
    %routingCost1[i,k,q] >= travelCost[i,w]*f[i,w,k]
    %f[i,w,k] = 1 -> routingCost1[i,k,q] = travelCost[i,w]
  );
%% Dasselbe, nur noch mal explizit für die Proceed Kosten    
constraint forall(q in 0..transportCapacity, i in customers, k in vehicles, w in facilities)(
    fProceedInt1[i,k,q] >= travelCost[i,w]*f[i,w,k]*100
    %fProceed1[i,k,q] >= travelCost[i,w]*f[i,w,k]
    %f[i,w,k] = 1 -> fProceed1[i,k,q] = travelCost[i,w]
  );
%%  Dasselbe, nur noch mal explizit für die Return Kosten    
  constraint forall(q in 0..transportCapacity, i in customers, k in vehicles, w in facilities)(
    fReturnInt1[i,k,q] >= travelCost[i,w]*f[i,w,k]*100
    %fReturn1[i,k,q] >= travelCost[i,w]*f[i,w,k]
    %f[i,w,k] = 1 -> fReturn1[i,k,q] = travelCost[i,w]
  );                    

%% M_NB_DP1 (3.3.3):
constraint forall(n in nodes, i in customers where n != i, q in 0..transportCapacity, k in vehicles)(
    fProceedInt1[n,k,q] >= ((travelCost[n,i]*f[n,i,k]*100)
    	 + (sum(q1 in 0..transportCapacity where q1 <= q)(routingCostInt1[i,k,q-q1]*demandProb[i,q1])
    	 + sum(q2 in 0..transportCapacity where q2 > q, w in facilities)(2*travelCost[i,w]*100*z[w,k]*demandProb[i,q2])
    	 + sum(q2 in 0..transportCapacity where q2 > q)(routingCostInt1[i,k,q-q2+transportCapacity]*demandProb[i,q2])))
       - BigM * (1-f[n,i,k])
    %fProceed1[n,k,q] >= ((travelCost[n,i]*f[n,i,k])
    %	 + sum(q1 in 0..transportCapacity where q1 <= q)(routingCost1[i,k,q-q1]*demandProb[i,q1])
    %	 + sum(q2 in 0..transportCapacity where q2 > q, w in facilities)(2*travelCost[i,w]*z[w,k]*demandProb[i,q2])
    %	 + sum(q2 in 0..transportCapacity where q2 > q)(routingCost1[i,k,q-q2+transportCapacity]*demandProb[i,q2]))
    %  - BigM * (1-f[n,i,k])
   % f[n,i,k] = 1 ->   fProceed1[n,k,q] == (travelCost[n,i])
   % 	 + sum(q1 in 0..transportCapacity where q1 <= q)(routingCost1[i,k,q-q1]*demandProb[i,q1])
   % 	 + sum(q2 in 0..transportCapacity where q2 > q, w in facilities)(2*travelCost[i,w]*z[w,k]*demandProb[i,q2])
   % 	 + sum(q2 in 0..transportCapacity where q2 > q)(routingCost1[i,k,q-q2+transportCapacity]*demandProb[i,q2])  
  );
  
%% M_NB_DP2 (3.3.4): 
constraint forall(n in nodes, i in customers where n != i, q in 0..transportCapacity, k in vehicles)(
    fReturnInt1[n,k,q] >= sum(w in facilities)((travelCost[n,w]+travelCost[w,i])*z[w,k]*100)
    	+ (sum(q1 in 0..transportCapacity)(routingCostInt1[i,k,transportCapacity-q1]*demandProb[i,q1]))
      - BigM * (1-f[n,i,k])
    %fReturn1[n,k,q] >= sum(w in facilities)((travelCost[n,w]+travelCost[w,i])*z[w,k])
    %	+ (sum(q1 in 0..transportCapacity)(routingCost1[i,k,transportCapacity-q1]*demandProb[i,q1]))
    %  - BigM * (1-f[n,i,k])
    %f[n,i,k]= 1 -> fReturn1[n,k,q] == sum(w in facilities)((travelCost[n,w]+travelCost[w,i])*z[w,k]) + sum(q1 in 0..transportCapacity)(routingCost1[i,k,transportCapacity-q1]*demandProb[i,q1])
  ); 

%% M_NB_DP3 (3.3.5a/b):
constraint forall(n in nodes, i in customers where n != i, q in 0..transportCapacity, k in vehicles)(
    routingCostInt1[n,k,q]>=(fProceedInt1[n,k,q]-BigM*(1-f[n,i,k]))-BigM*s1[n,k,q]
    %routingCost1[n,k,q]>=(fProceed1[n,k,q]-BigM*(1-f[n,i,k]))-BigM*s1[n,k,q]
    %s1[n,k,q]=0 /\ f[n,i,k] = 1 -> routingCost1[n,k,q] == fProceed1[n,k,q]
  );
constraint forall(n in nodes, i in customers where n != i, q in 0..transportCapacity, k in vehicles)(
    routingCostInt1[n,k,q]>=(fReturnInt1[n,k,q]-BigM*(1-f[n,i,k]))-BigM*(1-s1[n,k,q])
    %routingCost1[n,k,q]>=(fReturn1[n,k,q]-BigM*(1-f[n,i,k]))-BigM*(1-s1[n,k,q])
    %s1[n,k,q]=1 /\ f[n,i,k] = 1 -> routingCost1[n,k,q] == fReturn1[n,k,q]
  );  
%constraint forall(n in nodes, i in customers where n != i, q in 0..transportCapacity, k in vehicles)(
%    routingCost[n,i,k,q] == min()
%  );

% Test_NB_ErwarteterBedarfKleinerFahrzeugKapa:
%constraint forall(k in vehicles)(
%    sum(i in customers, n in nodes, q in 0..transportCapacity)(f[n,i,k]*demandProb[i,q]*q)<=transportCapacity
%  );

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% NB, die den "unbenötigten" Lösungsraum einschränken:

constraint forall(w in facilities, k in vehicles, q in 0..transportCapacity)(
    s1[w,k,q] == 0

  );


%NB Dezimalstellenbegrenzung:
%constraint forall(n in nodes, k in vehicles, q in 0..transportCapacity)(
%  routingCost1[n,k,q]*10 == routingCostInt1[n,k,q]
%);
%constraint forall(n in nodes, k in vehicles, q in 0..transportCapacity)(
%  fProceed1[n,k,q]*10 == fProceedInt1[n,k,q]
%);
%constraint forall(n in nodes, k in vehicles, q in 0..transportCapacity)(
%  fReturn1[n,k,q]*10 == fReturnInt1[n,k,q]
%);

%Debug

%constraint f[5,1,1] == 1;
%constraint f[4,6,1] == 1;
%constraint f[3,5,1] == 1;
%constraint f[2,3,1] == 1;
%constraint f[1,4,1] == 1;
%constraint f[6,2,1] == 1;
%constraint y[0]==1;
%constraint y[1]==0;